import requests
import json
import pandas as pd
from datetime import datetime
import time

class LoanPredictionClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200, response.json()
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}
    
    def get_latest_application(self):
        """Fetch the latest loan application from the database"""
        try:
            # Get applications with limit 1, sorted by creation date
            response = self.session.get(f"{self.base_url}/applications", params={
                "limit": 1,
                "offset": 0
            })
            
            if response.status_code == 200:
                data = response.json()
                if data["items"]:
                    return data["items"][0]
                else:
                    return None
            else:
                print(f"Error fetching applications: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to API: {e}")
            return None
    
    def prepare_prediction_data(self, application):
        """Prepare application data for prediction"""
        if not application:
            return None
        
        # Map database fields to prediction request format
        prediction_data = {
            "gender": application["gender"],
            "married": application["married"],
            "dependents": application["dependents"],
            "education": application["education"],
            "self_employed": application["self_employed"],
            "applicant_income": application["applicant_income"],
            "coapplicant_income": application["coapplicant_income"],
            "loan_amount": application["loan_amount"],
            "loan_amount_term": application["loan_amount_term"],
            "credit_history": application["credit_history"],
            "property_area": application["property_area"]
        }
        
        return prediction_data
    
    def make_prediction(self, prediction_data):
        """Make a loan prediction using the API"""
        try:
            response = self.session.post(
                f"{self.base_url}/predict",
                json=prediction_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error making prediction: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to API: {e}")
            return None
    
    def save_prediction_result(self, application, prediction_result, filename="prediction_results.json"):
        """Save prediction results to a file"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "application": application,
            "prediction": prediction_result
        }
        
        try:
            # Load existing results if file exists
            try:
                with open(filename, 'r') as f:
                    results = json.load(f)
            except FileNotFoundError:
                results = []
            
            # Add new result
            results.append(result)
            
            # Save updated results
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"Prediction result saved to {filename}")
        except Exception as e:
            print(f"Error saving prediction result: {e}")
    
    def run_prediction_pipeline(self):
        """Run the complete prediction pipeline"""
        print("=== Loan Prediction Pipeline ===")
        
        # Step 1: Health check
        print("1. Checking API health...")
        is_healthy, health_data = self.health_check()
        if not is_healthy:
            print("❌ API is not available")
            print(f"Error: {health_data}")
            return False
        
        print("✅ API is healthy")
        print(f"Model loaded: {health_data.get('data', {}).get('model_loaded', False)}")
        
        # Step 2: Fetch latest application
        print("\n2. Fetching latest loan application...")
        application = self.get_latest_application()
        if not application:
            print("❌ No applications found in database")
            return False
        
        print("✅ Latest application fetched")
        print(f"Loan ID: {application['loan_id']}")
        print(f"Applicant: {application['gender']}, {application['education']}")
        print(f"Income: ${application['applicant_income']:,.2f}")
        
        # Step 3: Prepare prediction data
        print("\n3. Preparing prediction data...")
        prediction_data = self.prepare_prediction_data(application)
        if not prediction_data:
            print("❌ Failed to prepare prediction data")
            return False
        
        print("✅ Prediction data prepared")
        
        # Step 4: Make prediction
        print("\n4. Making loan prediction...")
        prediction_result = self.make_prediction(prediction_data)
        if not prediction_result:
            print("❌ Failed to make prediction")
            return False
        
        print("✅ Prediction completed")
        print(f"Predicted Status: {prediction_result['predicted_status']}")
        print(f"Confidence Score: {prediction_result['confidence_score']:.4f}")
        print(f"Probability Approved: {prediction_result['probability_approved']:.4f}")
        
        # Step 5: Save results
        print("\n5. Saving prediction results...")
        self.save_prediction_result(application, prediction_result)
        
        # Step 6: Display feature importance
        if 'feature_importance' in prediction_result:
            print("\n6. Feature Importance:")
            feature_importance = prediction_result['feature_importance']
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            for feature, importance in sorted_features[:5]:
                print(f"   {feature}: {importance:.4f}")
        
        print("\n=== Pipeline Complete ===")
        return True

def main():
    """Main function to run the prediction pipeline"""
    client = LoanPredictionClient()
    
    # Run the pipeline
    success = client.run_prediction_pipeline()
    
    if success:
        print("🎉 Prediction pipeline completed successfully!")
    else:
        print("❌ Prediction pipeline failed!")
    
    return success

if __name__ == "__main__":
    main() 