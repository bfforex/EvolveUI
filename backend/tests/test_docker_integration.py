import pytest
import subprocess
import yaml
import json
import os
import sys
sys.path.append('..')

class TestDockerIntegration:
    """Test suite for Docker environment and configuration"""
    
    def test_docker_compose_syntax(self):
        """Test Docker compose file has valid syntax"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        # Test that file exists
        assert os.path.exists(compose_path), "docker-compose.yml not found"
        
        # Test that it's valid YAML
        with open(compose_path, 'r') as f:
            try:
                compose_config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in docker-compose.yml: {e}")
        
        # Test required services exist
        assert 'services' in compose_config, "No services section in docker-compose.yml"
        services = compose_config['services']
        
        required_services = ['chromadb', 'backend', 'frontend']
        for service in required_services:
            assert service in services, f"Required service '{service}' not found"
    
    def test_chromadb_service_configuration(self):
        """Test ChromaDB service configuration"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        chromadb_service = compose_config['services']['chromadb']
        
        # Test image
        assert chromadb_service['image'] == 'chromadb/chroma:latest'
        
        # Test ports
        assert '8000:8000' in chromadb_service['ports']
        
        # Test volumes
        volumes = chromadb_service['volumes']
        assert any('chromadb_data:/data' in vol for vol in volumes)
        
        # Test environment variables
        env = chromadb_service['environment']
        assert 'CHROMA_DB_IMPL=duckdb+parquet' in env
        assert 'CHROMA_PERSIST_DIR=/data' in env
        
        # Test health check
        assert 'healthcheck' in chromadb_service
        healthcheck = chromadb_service['healthcheck']
        assert 'curl' in ' '.join(healthcheck['test'])
        assert '/api/v1/heartbeat' in ' '.join(healthcheck['test'])
    
    def test_backend_service_configuration(self):
        """Test backend service configuration"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        backend_service = compose_config['services']['backend']
        
        # Test build context
        assert backend_service['build']['context'] == './backend'
        assert backend_service['build']['dockerfile'] == 'Dockerfile'
        
        # Test ports
        assert '8001:8000' in backend_service['ports']
        
        # Test environment variables
        env = backend_service['environment']
        ollama_host = next((e for e in env if 'OLLAMA_HOST' in e), None)
        assert ollama_host is not None
        assert 'host.docker.internal:11434' in ollama_host
        
        chromadb_host = next((e for e in env if 'CHROMADB_HOST' in e), None)
        assert chromadb_host is not None
        assert 'chromadb' in chromadb_host
        
        # Test depends_on
        assert 'depends_on' in backend_service
        assert 'chromadb' in backend_service['depends_on']
        assert backend_service['depends_on']['chromadb']['condition'] == 'service_healthy'
        
        # Test volumes for conversations.json
        volumes = backend_service['volumes']
        conversations_volume = next((v for v in volumes if 'conversations.json' in v), None)
        assert conversations_volume is not None
    
    def test_frontend_service_configuration(self):
        """Test frontend service configuration"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        frontend_service = compose_config['services']['frontend']
        
        # Test build context
        assert frontend_service['build']['context'] == './frontend'
        assert frontend_service['build']['dockerfile'] == 'Dockerfile'
        
        # Test ports
        assert '3000:80' in frontend_service['ports']
        
        # Test environment variables
        env = frontend_service['environment']
        backend_url = next((e for e in env if 'REACT_APP_BACKEND_URL' in e), None)
        assert backend_url is not None
        assert 'localhost:8001' in backend_url
        
        # Test depends_on
        assert 'depends_on' in frontend_service
        assert 'backend' in frontend_service['depends_on']
        assert frontend_service['depends_on']['backend']['condition'] == 'service_healthy'
    
    def test_docker_network_configuration(self):
        """Test Docker network configuration"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Test network exists
        assert 'networks' in compose_config
        networks = compose_config['networks']
        assert 'evolveui-network' in networks
        
        # Test network configuration
        evolveui_network = networks['evolveui-network']
        assert evolveui_network['driver'] == 'bridge'
        assert 'ipam' in evolveui_network
        assert 'config' in evolveui_network['ipam']
        
        # Test all services use the network
        services = compose_config['services']
        for service_name, service_config in services.items():
            assert 'networks' in service_config
            assert 'evolveui-network' in service_config['networks']
    
    def test_docker_volumes_configuration(self):
        """Test Docker volumes configuration"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Test volumes exist
        assert 'volumes' in compose_config
        volumes = compose_config['volumes']
        
        required_volumes = ['backend_logs', 'chromadb_data']
        for volume in required_volumes:
            assert volume in volumes
            assert volumes[volume]['driver'] == 'local'
    
    def test_docker_compose_validation(self):
        """Test Docker compose file validates correctly"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        try:
            result = subprocess.run(
                ['docker', 'compose', '-f', compose_path, 'config', '--quiet'],
                capture_output=True,
                text=True,
                cwd='/home/runner/work/EvolveUI/EvolveUI'
            )
            
            # Should exit with code 0 for valid config
            assert result.returncode == 0, f"Docker compose validation failed: {result.stderr}"
            
        except FileNotFoundError:
            pytest.skip("Docker not available in test environment")
    
    def test_backend_dockerfile_exists(self):
        """Test backend Dockerfile exists and has required content"""
        dockerfile_path = '/home/runner/work/EvolveUI/EvolveUI/backend/Dockerfile'
        
        assert os.path.exists(dockerfile_path), "Backend Dockerfile not found"
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Test basic Dockerfile structure
        assert 'FROM python:' in content, "No Python base image specified"
        assert 'COPY requirements.txt' in content or 'pip install' in content, "No dependency installation"
        assert 'EXPOSE' in content, "No port exposed"
        assert 'CMD' in content or 'ENTRYPOINT' in content, "No startup command"
    
    def test_frontend_dockerfile_exists(self):
        """Test frontend Dockerfile exists and has required content"""
        dockerfile_path = '/home/runner/work/EvolveUI/EvolveUI/frontend/Dockerfile'
        
        assert os.path.exists(dockerfile_path), "Frontend Dockerfile not found"
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Test multi-stage build structure
        assert 'FROM node:' in content, "No Node.js base image for build stage"
        assert 'npm ci' in content or 'npm install' in content, "No npm dependency installation command"
        assert 'npm run build' in content, "No build command"
        assert 'FROM nginx:' in content, "No nginx base image for serve stage"
    
    def test_resource_limits(self):
        """Test resource limits are properly configured"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        services = compose_config['services']
        
        # Test that critical services have resource limits
        critical_services = ['chromadb', 'backend']
        for service_name in critical_services:
            service = services[service_name]
            assert 'deploy' in service, f"No deploy config for {service_name}"
            assert 'resources' in service['deploy'], f"No resource config for {service_name}"
            
            resources = service['deploy']['resources']
            assert 'limits' in resources, f"No resource limits for {service_name}"
            assert 'memory' in resources['limits'], f"No memory limit for {service_name}"
    
    def test_health_checks(self):
        """Test health checks are properly configured"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        services = compose_config['services']
        
        # Test that all services have health checks
        for service_name, service_config in services.items():
            assert 'healthcheck' in service_config, f"No health check for {service_name}"
            
            healthcheck = service_config['healthcheck']
            assert 'test' in healthcheck, f"No health check test for {service_name}"
            assert 'interval' in healthcheck, f"No health check interval for {service_name}"
            assert 'timeout' in healthcheck, f"No health check timeout for {service_name}"
            assert 'retries' in healthcheck, f"No health check retries for {service_name}"

class TestChromaDBConfiguration:
    """Test suite for ChromaDB configuration and deprecation fixes"""
    
    def test_chromadb_environment_variables(self):
        """Test ChromaDB environment variables are properly set"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        chromadb_env = compose_config['services']['chromadb']['environment']
        
        # Test required environment variables
        required_env_vars = [
            'CHROMA_DB_IMPL=duckdb+parquet',
            'CHROMA_PERSIST_DIR=/data'
        ]
        
        for env_var in required_env_vars:
            assert env_var in chromadb_env, f"Missing environment variable: {env_var}"
        
        # Test authentication configuration (for production)
        auth_vars = [var for var in chromadb_env if 'AUTH' in var]
        assert len(auth_vars) > 0, "No authentication configuration found"
    
    def test_chromadb_port_configuration(self):
        """Test ChromaDB is configured on correct port"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        chromadb_service = compose_config['services']['chromadb']
        
        # Test port mapping
        ports = chromadb_service['ports']
        assert '8000:8000' in ports, "ChromaDB not configured on port 8000"
    
    def test_chromadb_data_persistence(self):
        """Test ChromaDB data persistence configuration"""
        compose_path = '/home/runner/work/EvolveUI/EvolveUI/docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        chromadb_service = compose_config['services']['chromadb']
        
        # Test volume mounting
        volumes = chromadb_service['volumes']
        data_volume = next((v for v in volumes if '/data' in v), None)
        assert data_volume is not None, "No data volume mounted for ChromaDB"
        assert 'chromadb_data:/data' in data_volume, "ChromaDB data not properly persisted"
        
        # Test environment variable for persist directory
        env = chromadb_service['environment']
        persist_dir = next((e for e in env if 'CHROMA_PERSIST_DIR' in e), None)
        assert persist_dir is not None, "CHROMA_PERSIST_DIR not set"
        assert '/data' in persist_dir, "Persist directory not set to /data"

if __name__ == "__main__":
    pytest.main([__file__])