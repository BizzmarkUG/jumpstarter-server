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

	"k8s.io/apimachinery/pkg/fields"
	"k8s.io/apimachinery/pkg/labels"
	"k8s.io/apiserver/pkg/authentication/authenticator"
	"k8s.io/apiserver/pkg/authentication/user"
	"k8s.io/apiserver/pkg/authorization/authorizer"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

// SimpleAuthenticator provides basic authentication for standalone mode
type SimpleAuthenticator struct {
	prefix string
}

// AuthenticateToken implements authenticator.Token interface
func (a *SimpleAuthenticator) AuthenticateToken(ctx context.Context, token string) (*authenticator.Response, bool, error) {
	// In standalone mode, we accept any token and create a user based on the prefix
	// In a production environment, you would validate the token properly
	
	if token == "" {
		return nil, false, nil
	}
	
	// Create a user info object
	userInfo := &user.DefaultInfo{
		Name:   fmt.Sprintf("%s:user", a.prefix),
		UID:    fmt.Sprintf("%s:uid", a.prefix),
		Groups: []string{fmt.Sprintf("%s:users", a.prefix)},
	}
	
	return &authenticator.Response{
		User: userInfo,
	}, true, nil
}

// AuthenticateContext implements authentication.ContextAuthenticator interface
func (a *SimpleAuthenticator) AuthenticateContext(ctx context.Context) (*authenticator.Response, bool, error) {
	// For standalone mode, just create a default user
	userInfo := &user.DefaultInfo{
		Name:   fmt.Sprintf("%s:user", a.prefix),
		UID:    fmt.Sprintf("%s:uid", a.prefix),
		Groups: []string{fmt.Sprintf("%s:users", a.prefix)},
	}
	
	return &authenticator.Response{
		User: userInfo,
	}, true, nil
}

// SimpleAuthorizer provides basic authorization for standalone mode
type SimpleAuthorizer struct{}

// Authorize implements authorizer.Authorizer interface
func (a *SimpleAuthorizer) Authorize(ctx context.Context, attrs authorizer.Attributes) (authorizer.Decision, string, error) {
	// In standalone mode, we allow all operations
	// In a production environment, you would implement proper authorization logic
	return authorizer.DecisionAllow, "allowed in standalone mode", nil
}

// SimpleAttributesGetter provides metadata attributes for authorization
type SimpleAttributesGetter struct{}

// GetAttributes extracts attributes from the request context
func (g *SimpleAttributesGetter) GetAttributes(ctx context.Context, obj client.Object) map[string]string {
	// Return empty attributes for standalone mode
	// In a real implementation, you might extract namespace, resource type, etc.
	return map[string]string{}
}

// ContextAttributes implements authorization.ContextAttributesGetter interface
func (g *SimpleAttributesGetter) ContextAttributes(ctx context.Context, user user.Info) (authorizer.Attributes, error) {
	// Return basic attributes for standalone mode
	return &simpleAttributes{
		user: user,
	}, nil
}

// simpleAttributes implements authorizer.Attributes
type simpleAttributes struct {
	user user.Info
}

func (a *simpleAttributes) GetUser() user.Info                { return a.user }
func (a *simpleAttributes) GetVerb() string                   { return "get" }
func (a *simpleAttributes) IsReadOnly() bool                  { return false }
func (a *simpleAttributes) GetNamespace() string              { return "" }
func (a *simpleAttributes) GetResource() string               { return "" }
func (a *simpleAttributes) GetSubresource() string            { return "" }
func (a *simpleAttributes) GetName() string                   { return "" }
func (a *simpleAttributes) GetAPIGroup() string               { return "" }
func (a *simpleAttributes) GetAPIVersion() string             { return "" }
func (a *simpleAttributes) IsResourceRequest() bool           { return true }
func (a *simpleAttributes) GetPath() string                   { return "" }
func (a *simpleAttributes) GetFieldSelector() (fields.Requirements, error) { return nil, nil }
func (a *simpleAttributes) GetLabelSelector() (labels.Requirements, error) { return nil, nil }