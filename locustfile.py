
import json
import random
from locust import HttpUser, task, between


class APITestUser(HttpUser):
    
    host = "https://briefly-backend-459260001744.us-east1.run.app"
    auth_token = None
    if not auth_token:
        exit(1)  # Ensure auth token is set before running tests
    
    # Wait time between requests (1-3 seconds)
    wait_time = between(1, 3)
    
    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        self.sample_assets = [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 150,
                "units_held": 10,
                "is_hedge": False,
                "hedges_asset": None
            },
            {
                "ticker": "GOOGL",
                "name": "Alphabet Inc.",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 2500,
                "units_held": 5,
                "is_hedge": False,
                "hedges_asset": None
            },
            {
                "ticker": "JNJ",
                "name": "Johnson & Johnson",
                "asset_type": "stock",
                "sector": "Healthcare",
                "region": "US",
                "market_price": 160,
                "units_held": 15,
                "is_hedge": False,
                "hedges_asset": None
            },
            {
                "ticker": "XOM",
                "name": "Exxon Mobil",
                "asset_type": "stock",
                "sector": "Energy",
                "region": "Global",
                "market_price": 100,
                "units_held": 20,
                "is_hedge": False,
                "hedges_asset": None
            },
            {
                "ticker": "TREASURY",
                "name": "US Treasury Bond",
                "asset_type": "bond",
                "sector": "Government Bonds",
                "region": "US",
                "market_price": 1000,
                "units_held": 5,
                "is_hedge": False,
                "hedges_asset": None
            }
        ]
        
        self.sample_profile = {
            "portfolio_id": None,  # Can be None for all portfolios
            "short_term_objectives": ["Growth", "Income"],
            "long_term_objectives": ["Retirement", "Wealth Building"],
            "sector_preferences": ["Technology", "Healthcare", "Energy"],
            "regional_preferences": ["US", "Europe", "Global"],
            "asset_preferences": ["Stocks", "Bonds", "Options"]
        }
        
        # IDS USED to track create items to be used in deletion tests
        self.created_portfolios = []
        self.created_archives = []
        self.created_profiles = []

    
    # PORTFLIO ENDPOINTS
    @task(3)
    def get_portfolios(self):
        """GET /portfolios - Retrieve user portfolios"""
        with self.client.get(
            "/portfolios",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if isinstance(data, list):
                        # Store portfolio IDs for other tests
                        self.created_portfolios = [p['id'] for p in data if 'id' in p]
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"GET portfolios failed with status {response.status_code}")

    @task(4)
    def create_portfolio(self):
        import time
        portfolio_data = {
            "name": f"Test Portfolio {int(time.time())}-{random.randint(100, 999)}",
            "assets": random.sample(self.sample_assets, random.randint(1, 3))
        } # Randomly select 1-3 assets from sample to create a portfolio
        
        with self.client.post(
            "/portfolios",
            headers=self.headers,
            data=json.dumps(portfolio_data),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if 'id' in data:
                        self.created_portfolios.append(data['id']) # Store created portfolio ID to delete later
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                try:
                    error_detail = response.json()
                    response.failure(f"POST portfolio failed with status {response.status_code}: {error_detail}")
                except:
                    response.failure(f"POST portfolio failed with status {response.status_code}: {response.text[:200]}")

    @task(1)
    def get_portfolio_by_id(self):
        """GET /portfolios/{id} - Get specific portfolio"""
        if not self.created_portfolios:
            return
            
        portfolio_id = random.choice(self.created_portfolios)
        with self.client.get(
            f"/portfolios/{portfolio_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Expected for non-existent portfolios
            else:
                response.failure(f"GET portfolio by ID failed with status {response.status_code}")

    @task(1)
    def update_portfolio(self):
        if not self.created_portfolios:
            return
            
        portfolio_id = random.choice(self.created_portfolios)
        import time
        updated_data = {
            "name": f"Updated Portfolio {int(time.time())}-{random.randint(100, 999)}",
            "assets": random.sample(self.sample_assets, random.randint(1, 3))
        }
        
        with self.client.put(
            f"/portfolios/{portfolio_id}",
            headers=self.headers,
            data=json.dumps(updated_data),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # for non existent portfolios
            else:
                response.failure(f"PUT portfolio failed with status {response.status_code}")

    @task(1)
    def delete_portfolio(self):
        if not self.created_portfolios:
            return
            
        portfolio_id = self.created_portfolios.pop()
        with self.client.delete(
            f"/portfolios/{portfolio_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Expected for non-existent portfolios
            else:
                response.failure(f"DELETE portfolio failed with status {response.status_code}")

    # ARCHIVE ENDPOINTS
    @task(2)
    def get_archives(self):
        with self.client.get(
            "/archives",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self.created_archives = [a['id'] for a in data if 'id' in a]
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"GET archives failed with status {response.status_code}")

    @task(1)
    def create_archive(self):
        if not self.created_portfolios:
            return
            
        archive_data = {
            "portfolio_id": random.choice(self.created_portfolios),
            "original_question": f"Test question {random.randint(1000, 9999)}",
            "openai_response": "This is a test response from OpenAI"
        }
        
        with self.client.post(
            "/archives",
            headers=self.headers,
            data=json.dumps(archive_data),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if 'id' in data:
                        self.created_archives.append(data['id'])
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"POST archive failed with status {response.status_code}")

    @task(1)
    def get_archived_response(self):
        if not self.created_archives:
            return
            
        archive_id = random.choice(self.created_archives)
        with self.client.get(
            f"/responses/{archive_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Expected for non-existent archives
            else:
                response.failure(f"GET archived response failed with status {response.status_code}")

    @task(1)
    def delete_archive(self):
        if not self.created_archives:
            return
            
        archive_id = self.created_archives.pop()
        with self.client.delete(
            f"/archives/{archive_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Expected for non-existent archives
            else:
                response.failure(f"DELETE archive failed with status {response.status_code}")

    @task(1)
    def delete_all_archives(self):
        with self.client.delete(
            "/archives",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                self.created_archives.clear()  # Clear local cache
            elif response.status_code == 500:
                response.failure("Server error deleting all archives")
            else:
                response.failure(f"DELETE all archives failed with status {response.status_code}")

    # PROFILE ENDPOINTS

    @task(2)
    def get_profiles(self):
        with self.client.get(
            "/profiles/",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self.created_profiles = [p['id'] for p in data if 'id' in p]
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"GET profiles failed with status {response.status_code}")

    @task(1)
    def create_profile(self):
        profile_data = {
            **self.sample_profile,
            "portfolio_id": random.choice(self.created_portfolios) if self.created_portfolios else None
        }
        
        with self.client.post(
            "/profiles/",
            headers=self.headers,
            data=json.dumps(profile_data),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if 'id' in data:
                        self.created_profiles.append(data['id'])
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"POST profile failed with status {response.status_code}")

    @task(1)
    def get_profile_by_id(self):
        if not self.created_profiles:
            return
            
        profile_id = random.choice(self.created_profiles)
        with self.client.get(
            f"/profiles/{profile_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Expected for non-existent profiles
            else:
                response.failure(f"GET profile by ID failed with status {response.status_code}")

    @task(1)
    def update_profile(self):
        if not self.created_profiles:
            return
            
        profile_id = random.choice(self.created_profiles)
        updated_profile = {
            **self.sample_profile,
            "short_term_objectives": ["Updated Growth", "Updated Income"],
            "portfolio_id": random.choice(self.created_portfolios) if self.created_portfolios else None
        }
        
        with self.client.put(
            f"/profiles/{profile_id}",
            headers=self.headers,
            data=json.dumps(updated_profile),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Expected for non-existent profiles
            else:
                response.failure(f"PUT profile failed with status {response.status_code}")

    @task(1)
    def delete_profile(self):
        if not self.created_profiles:
            return
            
        profile_id = self.created_profiles.pop()
        with self.client.delete(
            f"/profiles/{profile_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Expected for non-existent profiles
            else:
                response.failure(f"DELETE profile failed with status {response.status_code}")


