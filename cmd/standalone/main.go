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

package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/go-logr/logr"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	"github.com/jumpstarter-dev/jumpstarter-controller/internal/standalone"

func main() {
	var configFile string
	var enableHTTP2 bool
	var controllerAddr string
	var routerAddr string

	flag.StringVar(&configFile, "config", "/etc/jumpstarter/config.yaml", "Path to configuration file")
	flag.BoolVar(&enableHTTP2, "enable-http2", false, "If set, HTTP/2 will be enabled for the servers")
	flag.StringVar(&controllerAddr, "controller-addr", ":8080", "Address for the controller service to bind to")
	flag.StringVar(&routerAddr, "router-addr", ":8090", "Address for the router service to bind to")

	opts := zap.Options{
		Development: true,
	}
	opts.BindFlags(flag.CommandLine)
	flag.Parse()

	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))
	logger := ctrl.Log.WithName("standalone")
	ctx := logr.NewContext(context.Background(), logger)

	logger.Info("Starting jumpstarter in standalone mode",
		"config", configFile,
		"controller-addr", controllerAddr,
		"router-addr", routerAddr)

	// Create standalone server
	server, err := standalone.NewServer(ctx, standalone.Config{
		ConfigFile:     configFile,
		ControllerAddr: controllerAddr,
		RouterAddr:     routerAddr,
		EnableHTTP2:    enableHTTP2,
	})
	if err != nil {
		logger.Error(err, "Failed to create standalone server")
		os.Exit(1)
	}

	// Start the server
	if err := server.Start(ctx); err != nil {
		logger.Error(err, "Failed to start standalone server")
		os.Exit(1)
	}

	// Wait for termination signal
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	sig := <-sigs
	logger.Info("Received signal, shutting down", "signal", sig)

	// Graceful shutdown
	if err := server.Stop(ctx); err != nil {
		logger.Error(err, "Error during shutdown")
		os.Exit(1)
	}

	fmt.Println("Shutdown completed")
}
