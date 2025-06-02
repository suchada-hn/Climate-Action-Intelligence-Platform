"""
Test script to verify the Climate Action Intelligence Platform setup
"""
import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from config import settings
        print("✅ Config module imported successfully")
        print(f"   - IBM Cloud URL: {settings.IBM_CLOUD_URL}")
        print(f"   - OpenWeather API configured: {'Yes' if settings.OPENWEATHER_API_KEY else 'No'}")
    except Exception as e:
        print(f"❌ Error importing config: {e}")
        return False
    
    try:
        from backend.watsonx_integration.watsonx_client import WatsonxClient
        print("✅ WatsonX client imported successfully")
    except Exception as e:
        print(f"❌ Error importing WatsonX client: {e}")
        return False
    
    try:
        from backend.rag_system.climate_rag import ClimateRAGSystem
        print("✅ RAG system imported successfully")
    except Exception as e:
        print(f"❌ Error importing RAG system: {e}")
        return False
    
    try:
        from backend.data_processors.climate_data_fetcher import ClimateDataFetcher
        print("✅ Data fetcher imported successfully")
    except Exception as e:
        print(f"❌ Error importing data fetcher: {e}")
        return False
    
    try:
        from backend.data_processors.impact_tracker import ImpactTracker
        print("✅ Impact tracker imported successfully")
    except Exception as e:
        print(f"❌ Error importing impact tracker: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of key components"""
    print("\nTesting basic functionality...")
    
    try:
        from backend.data_processors.impact_tracker import ImpactTracker
        tracker = ImpactTracker()
        
        # Test tracking an action
        result = tracker.track_action("test_user", "led_bulb_replacement", 1.0)
        if 'error' not in result:
            print("✅ Impact tracker working correctly")
        else:
            print(f"❌ Impact tracker error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error testing impact tracker: {e}")
    
    try:
        from backend.data_processors.climate_data_fetcher import ClimateDataFetcher
        fetcher = ClimateDataFetcher()
        
        # Test fallback carbon calculation
        result = fetcher._get_fallback_carbon_estimate("electricity", 100, "kWh")
        if result.get('carbon_kg', 0) > 0:
            print("✅ Data fetcher working correctly")
        else:
            print("❌ Data fetcher not working properly")
            
    except Exception as e:
        print(f"❌ Error testing data fetcher: {e}")

def test_environment():
    """Test environment setup"""
    print("\nTesting environment...")
    
    # Check if data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
        print("✅ Created data directory")
    else:
        print("✅ Data directory exists")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} may not be compatible")

def main():
    """Run all tests"""
    print("🌍 Climate Action Intelligence Platform - Setup Test")
    print("=" * 60)
    
    test_environment()
    
    if test_imports():
        print("\n✅ All modules imported successfully!")
        test_basic_functionality()
        print("\n🎉 Setup test completed! The platform is ready to run.")
        print("\nTo start the application, run:")
        print("streamlit run app.py --server.port 12000 --server.address 0.0.0.0")
    else:
        print("\n❌ Some modules failed to import. Please check the error messages above.")

if __name__ == "__main__":
    main()