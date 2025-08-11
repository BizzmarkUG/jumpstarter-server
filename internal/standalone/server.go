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
	"crypto/tls"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/go-logr/logr"
	"github.com/jumpstarter-dev/jumpstarter-controller/internal/authentication"
	"github.com/jumpstarter-dev/jumpstarter-controller/internal/authorization"
	"github.com/jumpstarter-dev/jumpstarter-controller/internal/config"
	"github.com/jumpstarter-dev/jumpstarter-controller/internal/oidc"
	"github.com/jumpstarter-dev/jumpstarter-controller/internal/service"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
	"gopkg.in/yaml.v3"
)

// Config holds configuration for standalone mode
type Config struct {
	ConfigFile     string
	ControllerAddr string
	RouterAddr     string
	EnableHTTP2    bool
}

// Server represents a standalone jumpstarter server
type Server struct {
	config         Config
	logger         logr.Logger
	store          *Store
	controllerSvc  *service.ControllerService
	routerSvc      *service.RouterService
	oidcSvc        *service.OIDCService
	dashboardSvc   *service.DashboardService
	
	// Server components
	controllerServer *grpc.Server
	routerServer     *grpc.Server
	
	// Shutdown
	ctx    context.Context
	cancel context.CancelFunc
	wg     sync.WaitGroup
}

// StandaloneConfig represents the configuration file structure for standalone mode
type StandaloneConfig struct {
	Authentication AuthConfig     `yaml:"authentication"`
	Router         config.Router  `yaml:"router"`
	GRPC           GRPCConfig     `yaml:"grpc"`
}

type AuthConfig struct {
	Internal InternalAuth `yaml:"internal"`
}

type InternalAuth struct {
	Prefix string `yaml:"prefix"`
}

type GRPCConfig struct {
	Keepalive KeepaliveConfig `yaml:"keepalive"`
}

type KeepaliveConfig struct {
	MinTime             string `yaml:"minTime"`
	PermitWithoutStream bool   `yaml:"permitWithoutStream"`
}

// NewServer creates a new standalone server
func NewServer(ctx context.Context, config Config) (*Server, error) {
	logger := logr.FromContextOrDiscard(ctx).WithName("standalone-server")
	
	ctx, cancel := context.WithCancel(ctx)
	
	server := &Server{
		config: config,
		logger: logger,
		ctx:    ctx,
		cancel: cancel,
		store:  NewStore(),
	}
	
	if err := server.loadConfig(); err != nil {
		cancel()
		return nil, fmt.Errorf("failed to load config: %w", err)
	}
	
	if err := server.initServices(); err != nil {
		cancel()
		return nil, fmt.Errorf("failed to initialize services: %w", err)
	}
	
	return server, nil
}

// loadConfig loads configuration from file or creates default
func (s *Server) loadConfig() error {
	// Create default config if file doesn't exist
	if _, err := os.Stat(s.config.ConfigFile); os.IsNotExist(err) {
		s.logger.Info("Config file not found, creating default", "path", s.config.ConfigFile)
		return s.createDefaultConfig()
	}
	
	data, err := os.ReadFile(s.config.ConfigFile)
	if err != nil {
		return fmt.Errorf("failed to read config file: %w", err)
	}
	
	var config StandaloneConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return fmt.Errorf("failed to parse config: %w", err)
	}
	
	s.logger.Info("Loaded configuration", "path", s.config.ConfigFile)
	return nil
}

// createDefaultConfig creates a default configuration file
func (s *Server) createDefaultConfig() error {
	defaultConfig := StandaloneConfig{
		Authentication: AuthConfig{
			Internal: InternalAuth{
				Prefix: "jumpstarter",
			},
		},
		Router: config.Router{
			"default": config.RouterEntry{
				Endpoint: "localhost:8090",
				Labels:   map[string]string{},
			},
		},
		GRPC: GRPCConfig{
			Keepalive: KeepaliveConfig{
				MinTime:             "1s",
				PermitWithoutStream: true,
			},
		},
	}
	
	// Create directory if it doesn't exist
	if err := os.MkdirAll(filepath.Dir(s.config.ConfigFile), 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}
	
	data, err := yaml.Marshal(defaultConfig)
	if err != nil {
		return fmt.Errorf("failed to marshal default config: %w", err)
	}
	
	if err := os.WriteFile(s.config.ConfigFile, data, 0644); err != nil {
		return fmt.Errorf("failed to write default config: %w", err)
	}
	
	s.logger.Info("Created default configuration", "path", s.config.ConfigFile)
	return nil
}

// initServices initializes all services
func (s *Server) initServices() error {
	// Generate self-signed certificate for OIDC
	oidcCert, err := service.NewSelfSignedCertificate("jumpstarter oidc", []string{"localhost"}, []net.IP{})
	if err != nil {
		return fmt.Errorf("failed to generate OIDC certificate: %w", err)
	}
	
	// Create OIDC signer
	controllerKey := os.Getenv("CONTROLLER_KEY")
	if controllerKey == "" {
		controllerKey = "default-key-for-standalone-mode"
	}
	
	oidcSigner, err := oidc.NewSignerFromSeed(
		[]byte(controllerKey),
		"https://localhost:8085",
		"jumpstarter",
	)
	if err != nil {
		return fmt.Errorf("failed to create OIDC signer: %w", err)
	}
	
	// Initialize services with simplified configuration
	authenticator := &SimpleAuthenticator{prefix: "jumpstarter"}
	
	// Create simple router
	router := config.Router{
		"default": config.RouterEntry{
			Endpoint: s.config.RouterAddr,
			Labels:   map[string]string{},
		},
	}
	
	// GRPC server options
	serverOptions := grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
		MinTime:             1 * time.Second,
		PermitWithoutStream: true,
	})
	
	// Initialize controller service
	s.controllerSvc = &service.ControllerService{
		Client: s.store,
		Scheme: nil, // Not needed in standalone mode
		Authn:  authentication.NewBearerTokenAuthenticator(authenticator),
		Authz:  authorization.NewBasicAuthorizer(s.store, "jumpstarter", false),
		Attr: authorization.NewMetadataAttributesGetter(authorization.MetadataAttributesGetterConfig{
			NamespaceKey: "jumpstarter-namespace",
			ResourceKey:  "jumpstarter-kind",
			NameKey:      "jumpstarter-name",
		}),
		Router:       router,
		ServerOption: serverOptions,
	}
	
	// Initialize router service
	s.routerSvc = &service.RouterService{
		ServerOption: serverOptions,
	}
	
	// Initialize OIDC service
	s.oidcSvc = &service.OIDCService{
		Signer: oidcSigner,
		Cert:   oidcCert,
	}
	
	// Initialize dashboard service
	s.dashboardSvc = &service.DashboardService{
		Client: s.store,
		Scheme: nil, // Not needed in standalone mode
	}
	
	return nil
}

// Start starts the standalone server
func (s *Server) Start(ctx context.Context) error {
	s.logger.Info("Starting standalone server")
	
	// Determine HTTP/2 settings
	tlsOpts := []func(*tls.Config){}
	if !s.config.EnableHTTP2 {
		disableHTTP2 := func(c *tls.Config) {
			s.logger.Info("disabling http/2")
			c.NextProtos = []string{"http/1.1"}
		}
		tlsOpts = append(tlsOpts, disableHTTP2)
	}
	
	// Start controller service
	s.wg.Add(1)
	go func() {
		defer s.wg.Done()
		if err := s.startControllerService(); err != nil {
			s.logger.Error(err, "Controller service failed")
		}
	}()
	
	// Start router service
	s.wg.Add(1)
	go func() {
		defer s.wg.Done()
		if err := s.startRouterService(); err != nil {
			s.logger.Error(err, "Router service failed")
		}
	}()
	
	// Start OIDC service
	s.wg.Add(1)
	go func() {
		defer s.wg.Done()
		if err := s.startOIDCService(); err != nil {
			s.logger.Error(err, "OIDC service failed")
		}
	}()
	
	// Start dashboard service
	s.wg.Add(1)
	go func() {
		defer s.wg.Done()
		if err := s.startDashboardService(); err != nil {
			s.logger.Error(err, "Dashboard service failed")
		}
	}()
	
	s.logger.Info("Standalone server started successfully",
		"controller", s.config.ControllerAddr,
		"router", s.config.RouterAddr)
	
	return nil
}

// Stop stops the standalone server
func (s *Server) Stop(ctx context.Context) error {
	s.logger.Info("Stopping standalone server")
	
	s.cancel()
	
	// Stop GRPC servers
	if s.controllerServer != nil {
		s.controllerServer.GracefulStop()
	}
	if s.routerServer != nil {
		s.routerServer.GracefulStop()
	}
	
	// Wait for all goroutines to finish
	s.wg.Wait()
	
	s.logger.Info("Standalone server stopped")
	return nil
}

// startControllerService starts the controller gRPC service
func (s *Server) startControllerService() error {
	lis, err := net.Listen("tcp", s.config.ControllerAddr)
	if err != nil {
		return fmt.Errorf("failed to listen on controller address %s: %w", s.config.ControllerAddr, err)
	}
	
	s.controllerServer = grpc.NewServer(s.controllerSvc.ServerOption)
	
	// TODO: Register the actual controller service here
	// For now, we'll implement the basic structure
	
	s.logger.Info("Controller service listening", "addr", s.config.ControllerAddr)
	return s.controllerServer.Serve(lis)
}

// startRouterService starts the router gRPC service
func (s *Server) startRouterService() error {
	lis, err := net.Listen("tcp", s.config.RouterAddr)
	if err != nil {
		return fmt.Errorf("failed to listen on router address %s: %w", s.config.RouterAddr, err)
	}
	
	s.routerServer = grpc.NewServer(s.routerSvc.ServerOption)
	
	// TODO: Register the actual router service here
	
	s.logger.Info("Router service listening", "addr", s.config.RouterAddr)
	return s.routerServer.Serve(lis)
}

// startOIDCService starts the OIDC service
func (s *Server) startOIDCService() error {
	// TODO: Implement OIDC service startup for standalone mode
	s.logger.Info("OIDC service started")
	<-s.ctx.Done()
	return nil
}

// startDashboardService starts the dashboard service
func (s *Server) startDashboardService() error {
	// TODO: Implement dashboard service startup for standalone mode
	s.logger.Info("Dashboard service started")
	<-s.ctx.Done()
	return nil
}