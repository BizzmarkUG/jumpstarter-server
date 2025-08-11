/*
Copyright 2024.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package standalone

import (
	"context"
	"fmt"
	"reflect"
	"sync"
	"time"

	"k8s.io/apimachinery/pkg/api/meta"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/apimachinery/pkg/watch"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

// Store implements a simple in-memory store that satisfies the controller-runtime client interface
type Store struct {
	mu      sync.RWMutex
	objects map[string]runtime.Object
}

// NewStore creates a new in-memory store
func NewStore() *Store {
	return &Store{
		objects: make(map[string]runtime.Object),
	}
}

// objectKey creates a unique key for an object
func (s *Store) objectKey(obj runtime.Object) (string, error) {
	accessor, err := meta.Accessor(obj)
	if err != nil {
		return "", err
	}

	gvk := obj.GetObjectKind().GroupVersionKind()
	namespace := accessor.GetNamespace()
	name := accessor.GetName()

	if namespace != "" {
		return fmt.Sprintf("%s/%s/%s/%s", gvk.Group, gvk.Kind, namespace, name), nil
	}
	return fmt.Sprintf("%s/%s/%s", gvk.Group, gvk.Kind, name), nil
}

// Get retrieves an object from the store
func (s *Store) Get(ctx context.Context, key client.ObjectKey, obj client.Object, opts ...client.GetOption) error {
	s.mu.RLock()
	defer s.mu.RUnlock()

	gvk := obj.GetObjectKind().GroupVersionKind()
	var keyStr string
	if key.Namespace != "" {
		keyStr = fmt.Sprintf("%s/%s/%s/%s", gvk.Group, gvk.Kind, key.Namespace, key.Name)
	} else {
		keyStr = fmt.Sprintf("%s/%s/%s", gvk.Group, gvk.Kind, key.Name)
	}

	stored, exists := s.objects[keyStr]
	if !exists {
		return fmt.Errorf("object not found: %s", keyStr)
	}

	// Copy the stored object to the output object
	storedValue := reflect.ValueOf(stored)
	objValue := reflect.ValueOf(obj)
	if storedValue.Type().AssignableTo(objValue.Type()) {
		objValue.Elem().Set(storedValue.Elem())
	} else {
		return fmt.Errorf("type mismatch: cannot assign %T to %T", stored, obj)
	}
	return nil
}

// List retrieves a list of objects from the store
func (s *Store) List(ctx context.Context, list client.ObjectList, opts ...client.ListOption) error {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// This is a simplified implementation
	// In a real implementation, you'd filter by namespace, labels, etc.
	listOpts := &client.ListOptions{}
	for _, opt := range opts {
		opt.ApplyToList(listOpts)
	}

	// For now, return an empty list
	return nil
}

// Create creates a new object in the store
func (s *Store) Create(ctx context.Context, obj client.Object, opts ...client.CreateOption) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	accessor, err := meta.Accessor(obj)
	if err != nil {
		return err
	}

	// Set creation timestamp if not set
	creationTime := accessor.GetCreationTimestamp()
	if creationTime.IsZero() {
		accessor.SetCreationTimestamp(metav1.NewTime(time.Now()))
	}

	// Generate UID if not set
	if accessor.GetUID() == "" {
		accessor.SetUID(types.UID(fmt.Sprintf("uid-%d", time.Now().UnixNano())))
	}

	key, err := s.objectKey(obj)
	if err != nil {
		return err
	}

	if _, exists := s.objects[key]; exists {
		return fmt.Errorf("object already exists: %s", key)
	}

	s.objects[key] = obj.DeepCopyObject()
	return nil
}

// Delete removes an object from the store
func (s *Store) Delete(ctx context.Context, obj client.Object, opts ...client.DeleteOption) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	key, err := s.objectKey(obj)
	if err != nil {
		return err
	}

	if _, exists := s.objects[key]; !exists {
		return fmt.Errorf("object not found: %s", key)
	}

	delete(s.objects, key)
	return nil
}

// Update updates an object in the store
func (s *Store) Update(ctx context.Context, obj client.Object, opts ...client.UpdateOption) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	key, err := s.objectKey(obj)
	if err != nil {
		return err
	}

	if _, exists := s.objects[key]; !exists {
		return fmt.Errorf("object not found: %s", key)
	}

	s.objects[key] = obj.DeepCopyObject()
	return nil
}

// Patch patches an object in the store
func (s *Store) Patch(ctx context.Context, obj client.Object, patch client.Patch, opts ...client.PatchOption) error {
	// Simplified implementation - just call Update
	return s.Update(ctx, obj, &client.UpdateOptions{})
}

// DeleteAllOf deletes all objects matching the given options
func (s *Store) DeleteAllOf(ctx context.Context, obj client.Object, opts ...client.DeleteAllOfOption) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	gvk := obj.GetObjectKind().GroupVersionKind()
	prefix := fmt.Sprintf("%s/%s/", gvk.Group, gvk.Kind)

	for key := range s.objects {
		if key[:len(prefix)] == prefix {
			delete(s.objects, key)
		}
	}

	return nil
}

// Status returns a status writer for the object
func (s *Store) Status() client.StatusWriter {
	return &statusWriter{store: s}
}

// GroupVersionKindFor implements client.WithWatch interface
func (s *Store) GroupVersionKindFor(obj runtime.Object) (schema.GroupVersionKind, error) {
	gvk := obj.GetObjectKind().GroupVersionKind()
	if gvk.Empty() {
		return schema.GroupVersionKind{}, fmt.Errorf("missing group version kind for object")
	}
	return gvk, nil
}

// IsObjectNamespaced implements client.WithWatch interface
func (s *Store) IsObjectNamespaced(obj runtime.Object) (bool, error) {
	// Simple heuristic: if object has a namespace, it's namespaced
	accessor, err := meta.Accessor(obj)
	if err != nil {
		return false, err
	}
	return accessor.GetNamespace() != "", nil
}

// Watch implements client.WithWatch interface (simplified)
func (s *Store) Watch(ctx context.Context, list client.ObjectList, opts ...client.ListOption) (watch.Interface, error) {
	// Return a simple watch implementation that doesn't actually watch
	return &simpleWatch{}, nil
}

type simpleWatch struct{}

func (w *simpleWatch) Stop() {}

func (w *simpleWatch) ResultChan() <-chan watch.Event {
	ch := make(chan watch.Event)
	close(ch) // Close immediately as we don't implement real watching
	return ch
}

// Scheme returns the scheme (not needed for standalone mode)
func (s *Store) Scheme() *runtime.Scheme {
	return nil
}

// RESTMapper returns a REST mapper (not needed for standalone mode)
func (s *Store) RESTMapper() meta.RESTMapper {
	return nil
}

// statusWriter implements client.StatusWriter for the in-memory store
type statusWriter struct {
	store *Store
}

func (sw *statusWriter) Update(ctx context.Context, obj client.Object, opts ...client.SubResourceUpdateOption) error {
	return sw.store.Update(ctx, obj)
}

func (sw *statusWriter) Patch(ctx context.Context, obj client.Object, patch client.Patch, opts ...client.SubResourcePatchOption) error {
	return sw.store.Patch(ctx, obj, patch)
}

func (sw *statusWriter) Create(ctx context.Context, obj client.Object, subResource client.Object, opts ...client.SubResourceCreateOption) error {
	return sw.store.Create(ctx, obj)
}

// SubResource implements client.SubResourceClient (simplified)
func (s *Store) SubResource(subResource string) client.SubResourceClient {
	return &subResourceClient{store: s}
}

type subResourceClient struct {
	store *Store
}

func (src *subResourceClient) Get(ctx context.Context, obj client.Object, subResource client.Object, opts ...client.SubResourceGetOption) error {
	return src.store.Get(ctx, client.ObjectKeyFromObject(obj), obj)
}

func (src *subResourceClient) Create(ctx context.Context, obj client.Object, subResource client.Object, opts ...client.SubResourceCreateOption) error {
	return src.store.Create(ctx, obj)
}

func (src *subResourceClient) Update(ctx context.Context, obj client.Object, opts ...client.SubResourceUpdateOption) error {
	return src.store.Update(ctx, obj)
}

func (src *subResourceClient) Patch(ctx context.Context, obj client.Object, patch client.Patch, opts ...client.SubResourcePatchOption) error {
	return src.store.Patch(ctx, obj, patch)
}
