import json
import sys
import os
import csv

# Sample symptoms for fallback (only used if CSV files can't be read)
FALLBACK_SYMPTOMS = [
    "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering",
    "chills", "joint_pain", "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting",
    "burning_micturition", "fatigue", "weight_loss", "cough", "high_fever",
    "breathlessness", "sweating", "headache", "yellowish_skin", "dark_urine",
    "nausea", "loss_of_appetite", "abdominal_pain", "diarrhoea", "mild_fever",
    "yellowing_of_eyes", "swelled_lymph_nodes", "malaise", "blurred_vision"
]

# Fallback disease mapping
FALLBACK_DISEASE_MAP = {
    "Fungal infection": ["itching", "skin_rash", "nodal_skin_eruptions"],
    "Common Cold": ["continuous_sneezing", "shivering", "chills", "watering_from_eyes"],
    "Influenza": ["high_fever", "sweating", "chills", "fatigue", "headache"],
    "Typhoid": ["high_fever", "weakness", "abdominal_pain", "diarrhoea"],
    "Malaria": ["chills", "vomiting", "high_fever", "sweating", "headache"],
    "Pneumonia": ["chills", "cough", "high_fever", "breathlessness"],
    "Gastroenteritis": ["stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "diarrhoea"]
}

# Fallback descriptions and precautions (only used if CSV files can't be read)
FALLBACK_DESCRIPTIONS = {
    "Fungal infection": "A fungal infection that affects the skin, causing itching, rash, and nodular eruptions.",
    "Common Cold": "A viral infectious disease of the upper respiratory tract which primarily affects the nose.",
    "Influenza": "A viral infection that attacks your respiratory system — your nose, throat and lungs.",
    "Typhoid": "A bacterial infection that can spread throughout the body, affecting many organs.",
    "Malaria": "A serious and sometimes fatal disease caused by a parasite that commonly infects a certain type of mosquito.",
    "Pneumonia": "An infection that inflames air sacs in one or both lungs, which may fill with fluid.",
    "Gastroenteritis": "An intestinal infection marked by diarrhea, abdominal cramps, nausea or vomiting, and sometimes fever."
}

FALLBACK_PRECAUTIONS = {
    "Fungal infection": ["keep the affected area clean and dry", "use antifungal medications", "wear clean clothes", "avoid sharing personal items"],
    "Common Cold": ["get plenty of rest", "stay hydrated", "use a humidifier", "take over-the-counter cold medications"],
    "Influenza": ["get vaccinated", "wash hands frequently", "avoid close contact with sick people", "stay home if sick"],
    "Typhoid": ["get vaccinated", "wash hands thoroughly", "avoid raw foods", "drink purified water"],
    "Malaria": ["use mosquito nets", "use insect repellent", "take antimalarial drugs when traveling", "wear long sleeves and pants"],
    "Pneumonia": ["get vaccinated", "practice good hygiene", "avoid smoking", "maintain a healthy immune system"],
    "Gastroenteritis": ["stay hydrated", "rest", "avoid dairy products", "gradually reintroduce food"]
}

# Critical symptom-disease pairs (symptoms that strongly indicate specific diseases)
CRITICAL_SYMPTOM_DISEASE_PAIRS = {
    "patches_in_throat": ["AIDS"],
    "extra_marital_contacts": ["AIDS"],
    "blackheads": ["Acne"],
    "pus_filled_pimples": ["Acne", "Impetigo"],
    "swelling_of_stomach": ["Alcoholic hepatitis"],
    "history_of_alcohol_consumption": ["Alcoholic hepatitis"],
    "watering_from_eyes": ["Allergy", "Common Cold"],
    "continuous_sneezing": ["Allergy", "Common Cold"],
    "swelling_joints": ["Arthritis"],
    "painful_walking": ["Arthritis", "Osteoarthritis"],
    "mucoid_sputum": ["Bronchial Asthma"],
    "family_history": ["Bronchial Asthma", "Diabetes"],
    "breathlessness": ["Bronchial Asthma", "Pneumonia", "Heart attack"],
    "loss_of_balance": ["Cervical spondylosis", "Paroxysmal Positional Vertigo"],
    "red_spots_over_body": ["Chicken pox", "Dengue"],
    "yellowing_of_eyes": ["Chronic cholestasis", "Hepatitis A", "Hepatitis B", "Hepatitis C", "Hepatitis D", "Hepatitis E", "Jaundice"],
    "loss_of_taste": ["Covid"],
    "loss_of_smell": ["Covid"],
    "pain_behind_the_eyes": ["Dengue"],
    "blurred_and_distorted_vision": ["Diabetes", "Hypoglycemia"],
    "excessive_hunger": ["Diabetes", "Hyperthyroidism", "Hypoglycemia"],
    "polyuria": ["Diabetes"],
    "pain_during_bowel_movements": ["Dimorphic hemorrhoids(piles)"],
    "bloody_stool": ["Dimorphic hemorrhoids(piles)"],
    "burning_micturition": ["Drug Reaction", "Urinary tract infection"],
    "spotting_urination": ["Drug Reaction"],
    "dyschromic_patches": ["Fungal infection"],
    "acidity": ["GERD", "Peptic ulcer disease"],
    "chest_pain": ["GERD", "Heart attack", "Pneumonia"],
    "dehydration": ["Gastroenteritis"],
    "fluid_overload": ["Alcoholic hepatitis"],
    "coma": ["Hepatitis E"],
    "stomach_bleeding": ["Hepatitis E"],
    "lack_of_concentration": ["Hypertension"],
    "fast_heart_rate": ["Hyperthyroidism", "Pneumonia"],
    "abnormal_menstruation": ["Hyperthyroidism", "Hypothyroidism"],
    "drying_and_tingling_lips": ["Hypoglycemia"],
    "slurred_speech": ["Hypoglycemia"],
    "cold_hands_and_feet": ["Hypothyroidism"],
    "brittle_nails": ["Hypothyroidism"],
    "puffy_face_and_eyes": ["Hypothyroidism"],
    "enlarged_thyroid": ["Hypothyroidism"],
    "blister": ["Impetigo"],
    "red_sore_around_nose": ["Impetigo"],
    "yellow_crust_ooze": ["Impetigo"],
    "rusty_sputum": ["Pneumonia"],
    "altered_sensorium": ["Paralysis (brain hemorrhage)"],
    "spinning_movements": ["Paroxysmal Positional Vertigo"],
    "passage_of_gases": ["Peptic ulcer disease"],
    "internal_itching": ["Peptic ulcer disease"],
    "silver_like_dusting": ["Psoriasis"],
    "small_dents_in_nails": ["Psoriasis"],
    "inflammatory_nails": ["Psoriasis"],
    "blood_in_sputum": ["Tuberculosis"],
    "foul_smell_of urine": ["Urinary tract infection"],
    "continuous_feel_of_urine": ["Urinary tract infection"],
    "prominent_veins_on_calf": ["Varicose veins"],
    "swollen_blood_vessels": ["Varicose veins"]
}

try:
    # Try to import pandas and other libraries
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    
    USING_ML = True
    print("Using machine learning model with pandas/sklearn", file=sys.stderr)
except ImportError:
    # Fall back to basic pattern matching
    USING_ML = False
    print("Pandas/sklearn not available. Using fallback pattern matching.", file=sys.stderr)


def get_dataset_path(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '../../public/data', filename)


def get_dataset_path_backend(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(current_dir, '../../backend/dataset', filename)
    if os.path.exists(backend_path):
        return backend_path
    return os.path.join(current_dir, '../../public/data', filename)


def parse_csv_file(filename, fallback=None):
    """Generic function to parse CSV files with error handling"""
    try:
        file_path = get_dataset_path_backend(filename)
        
        if not os.path.exists(file_path):
            print(f"File {filename} not found at {file_path}", file=sys.stderr)
            return fallback
            
        result = {}
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f)
            # Skip header
            headers = next(csv_reader)
            
            for row in csv_reader:
                if not row:
                    continue
                
                key = row[0].strip()
                values = [val.strip() for val in row[1:] if val and val.strip().lower() != 'null']
                result[key] = values
                
        return result
    except Exception as e:
        print(f"Error parsing {filename}: {str(e)}", file=sys.stderr)
        return fallback


def parse_disease_description():
    """Parse disease_description.csv file"""
    try:
        file_path = get_dataset_path_backend('disease_description.csv')
        
        if not os.path.exists(file_path):
            print(f"Disease description file not found at {file_path}", file=sys.stderr)
            return FALLBACK_DESCRIPTIONS
            
        descriptions = {}
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f)
            # Skip header
            next(csv_reader)
            
            for row in csv_reader:
                if len(row) >= 2:
                    disease = row[0].strip()
                    description = row[1].strip()
                    descriptions[disease] = description
                    
        print(f"Successfully loaded {len(descriptions)} disease descriptions", file=sys.stderr)
        return descriptions
    except Exception as e:
        print(f"Error parsing disease descriptions: {str(e)}", file=sys.stderr)
        return FALLBACK_DESCRIPTIONS


def parse_disease_precautions():
    """Parse disease_precaution.csv file"""
    try:
        file_path = get_dataset_path_backend('disease_precaution.csv')
        
        if not os.path.exists(file_path):
            print(f"Disease precaution file not found at {file_path}", file=sys.stderr)
            return FALLBACK_PRECAUTIONS
            
        precautions = {}
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f)
            # Skip header
            next(csv_reader)
            
            for row in csv_reader:
                if len(row) >= 2:
                    disease = row[0].strip()
                    disease_precautions = [p.strip() for p in row[1:] if p and p.strip().lower() != 'null']
                    precautions[disease] = disease_precautions
                    
        print(f"Successfully loaded precautions for {len(precautions)} diseases", file=sys.stderr)
        return precautions
    except Exception as e:
        print(f"Error parsing disease precautions: {str(e)}", file=sys.stderr)
        return FALLBACK_PRECAUTIONS


def parse_symptom_severity():
    """Parse symptom_severity.csv file"""
    try:
        file_path = get_dataset_path_backend('symptom_severity.csv')
        
        if not os.path.exists(file_path):
            print(f"Symptom severity file not found at {file_path}", file=sys.stderr)
            return {}
            
        severity = {}
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f)
            # Skip header
            next(csv_reader)
            
            for row in csv_reader:
                if len(row) >= 2:
                    symptom = row[0].strip()
                    try:
                        severity_value = int(row[1].strip())
                        severity[symptom] = severity_value
                    except ValueError:
                        # Skip if severity is not a valid number
                        pass
                    
        print(f"Successfully loaded severity for {len(severity)} symptoms", file=sys.stderr)
        return severity
    except Exception as e:
        print(f"Error parsing symptom severity: {str(e)}", file=sys.stderr)
        return {}


def parse_dataset_csv():
    """Parse the dataset.csv file to extract disease-symptom mappings"""
    disease_symptom_map = {}
    all_symptoms = set()
    
    try:
        dataset_path = get_dataset_path_backend('dataset.csv')
        
        if not os.path.exists(dataset_path):
            print(f"Dataset file not found at {dataset_path}", file=sys.stderr)
            return FALLBACK_DISEASE_MAP, FALLBACK_SYMPTOMS
            
        with open(dataset_path, 'r') as f:
            csv_reader = csv.reader(f)
            # Skip header
            next(csv_reader)
            
            for row in csv_reader:
                if not row:
                    continue
                    
                disease = row[0].strip()
                symptoms = []
                
                # Process symptoms (start from index 1)
                for i in range(1, len(row)):
                    # Skip empty or 'null' values
                    if row[i] and row[i].strip().lower() != 'null':
                        symptom = row[i].strip()
                        symptoms.append(symptom)
                        all_symptoms.add(symptom)
                
                # Add or update disease-symptom mapping
                if disease in disease_symptom_map:
                    # Merge symptoms for the same disease (avoid duplicates)
                    existing_symptoms = set(disease_symptom_map[disease])
                    existing_symptoms.update(symptoms)
                    disease_symptom_map[disease] = list(existing_symptoms)
                else:
                    disease_symptom_map[disease] = symptoms
        
        print(f"Successfully parsed dataset.csv with {len(disease_symptom_map)} diseases and {len(all_symptoms)} unique symptoms", file=sys.stderr)
        return disease_symptom_map, sorted(list(all_symptoms))
    except Exception as e:
        print(f"Error parsing dataset.csv: {str(e)}", file=sys.stderr)
        return FALLBACK_DISEASE_MAP, FALLBACK_SYMPTOMS


# Load all data when module is imported
DISEASE_SYMPTOM_MAP, ALL_SYMPTOMS = parse_dataset_csv()
DISEASE_DESCRIPTIONS = parse_disease_description()
DISEASE_PRECAUTIONS = parse_disease_precautions()
SYMPTOM_SEVERITY = parse_symptom_severity()


def get_all_symptoms():
    """Get list of all symptoms"""
    if USING_ML:
        try:
            df = pd.read_csv(get_dataset_path('Training.csv'))
            
            # Get all symptom columns (excluding prognosis/disease column)
            symptom_cols = df.columns[:-1]
            
            # Get unique symptoms that are not empty
            all_symptoms = set()
            for col in symptom_cols:
                symptoms = df[col].dropna().unique()
                symptoms = [s for s in symptoms if s != '']
                all_symptoms.update(symptoms)
            
            # Add symptoms from dataset.csv
            all_symptoms.update(ALL_SYMPTOMS)
            
            # Convert to sorted list
            return sorted(list(all_symptoms))
        except Exception as e:
            print(f"Error getting symptoms from Training.csv: {str(e)}", file=sys.stderr)
            # Fall back to symptoms from dataset.csv
            return ALL_SYMPTOMS
    else:
        # Use symptoms from dataset.csv
        return ALL_SYMPTOMS


def predict(input_symptoms):
    """Predict disease based on symptoms"""
    if USING_ML:
        try:
            # Load datasets
            train_df = pd.read_csv(get_dataset_path('Training.csv'))
            test_df = pd.read_csv(get_dataset_path('Testing.csv'))
            
            # Prepare X and y for training
            X_train = train_df.drop('prognosis', axis=1)
            y_train = train_df['prognosis']
            
            # Train the model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Create vector for input symptoms
            input_vector = np.zeros(len(X_train.columns))
            for symptom in input_symptoms:
                if symptom in X_train.columns:
                    idx = X_train.columns.get_loc(symptom)
                    input_vector[idx] = 1
            
            # Predict disease
            disease = model.predict([input_vector])[0]
            
            # Get prediction probabilities and confidence
            probabilities = model.predict_proba([input_vector])[0]
            disease_idx = list(model.classes_).index(disease)
            confidence = probabilities[disease_idx] * 100
            
            result = {
                'disease': disease,
                'confidence': float(confidence)
            }
            
            # Add description if available
            if disease in DISEASE_DESCRIPTIONS:
                result['description'] = DISEASE_DESCRIPTIONS[disease]
            
            # Add precautions if available
            if disease in DISEASE_PRECAUTIONS:
                result['precautions'] = DISEASE_PRECAUTIONS[disease]
            
            return result
        except Exception as e:
            print(f"Error using ML model: {str(e)}", file=sys.stderr)
            # Fall back to improved pattern matching
            return predict_with_clinical_relevance(input_symptoms)
    else:
        # Use improved pattern matching
        return predict_with_clinical_relevance(input_symptoms)


def predict_with_clinical_relevance(input_symptoms):
    """Advanced pattern matching with clinical relevance scoring"""
    if not input_symptoms:
        return {
            "disease": "Unknown",
            "confidence": 0,
            "error": "No symptoms provided"
        }
    
    # Check if any critical symptoms are present that strongly indicate specific diseases
    critical_diseases = set()
    matched_critical_symptoms = {}
    
    for symptom in input_symptoms:
        if symptom in CRITICAL_SYMPTOM_DISEASE_PAIRS:
            for disease in CRITICAL_SYMPTOM_DISEASE_PAIRS[symptom]:
                critical_diseases.add(disease)
                if disease not in matched_critical_symptoms:
                    matched_critical_symptoms[disease] = []
                matched_critical_symptoms[disease].append(symptom)
    
    # Calculate scores for all diseases
    disease_scores = {}
    detailed_matches = {}
    
    for disease, symptoms in DISEASE_SYMPTOM_MAP.items():
        # Skip if no symptoms are defined for this disease
        if not symptoms:
            continue
            
        # Find matching symptoms
        matching = set(input_symptoms) & set(symptoms)
        
        if matching:
            # Calculate various scoring factors
            
            # 1. Severity score - sum of severity values of matching symptoms
            severity_score = sum(SYMPTOM_SEVERITY.get(symptom, 3) for symptom in matching)
            
            # 2. Coverage ratio - percentage of disease symptoms matched
            coverage_ratio = len(matching) / len(symptoms)
            
            # 3. Critical symptom bonus
            critical_bonus = 2.0 if disease in critical_diseases else 1.0
            
            # 4. Specific symptom weights
            # High specificity symptoms get higher weight 
            specificity_bonus = 0
            for symptom in matching:
                # If this symptom specifically points to fewer diseases, it's more specific
                if symptom in CRITICAL_SYMPTOM_DISEASE_PAIRS:
                    specificity = 1.0 / (len(CRITICAL_SYMPTOM_DISEASE_PAIRS[symptom]) + 1)
                    specificity_bonus += specificity
            
            # 5. Symptom count factor - more matching symptoms is better
            symptom_count_factor = min(1.0, len(matching) / 5)  # Cap at 5 symptoms
            
            # Final score calculation - weighted combination of factors
            # The weighting emphasizes:
            # 1. Critical symptoms that strongly indicate specific diseases
            # 2. Severity of the matching symptoms
            # 3. How many of the disease's key symptoms are present
            final_score = (
                (0.35 * severity_score / max(1, sum(SYMPTOM_SEVERITY.get(s, 3) for s in symptoms))) + 
                (0.25 * coverage_ratio) + 
                (0.15 * specificity_bonus) + 
                (0.25 * symptom_count_factor)
            ) * critical_bonus
            
            disease_scores[disease] = final_score
            detailed_matches[disease] = {
                "matching_symptoms": list(matching),
                "matching_count": len(matching),
                "total_symptoms": len(symptoms),
                "severity_score": severity_score,
                "coverage_ratio": coverage_ratio,
                "is_critical": disease in critical_diseases
            }
    
    # Find the disease with the highest score
    if disease_scores:
        predicted_disease = max(disease_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence as a percentage (0-100)
        confidence = min(disease_scores[predicted_disease] * 60, 98)  # Scale and cap confidence
        
        # Adjust confidence based on the number of input symptoms
        # If very few symptoms are provided, reduce confidence
        if len(input_symptoms) < 3:
            confidence = confidence * 0.7
        
        result = {
            "disease": predicted_disease,
            "confidence": confidence,
            "matching_symptoms": detailed_matches[predicted_disease]["matching_symptoms"],
            "matching_count": detailed_matches[predicted_disease]["matching_count"]
        }
        
        # Add description and precautions if available
        if predicted_disease in DISEASE_DESCRIPTIONS:
            result["description"] = DISEASE_DESCRIPTIONS[predicted_disease]
        
        if predicted_disease in DISEASE_PRECAUTIONS:
            result["precautions"] = DISEASE_PRECAUTIONS[predicted_disease]
        
        return result
    else:
        # Fall back to the basic pattern matching if no matches were found
        return predict_with_pattern_matching(input_symptoms)


def predict_with_severity(input_symptoms):
    """Pattern matching algorithm using dataset.csv and symptom severity"""
    max_score = 0
    predicted_disease = "Unknown"
    matched_symptoms = {}
    
    # Calculate the total severity score of input symptoms
    input_severity_total = sum(SYMPTOM_SEVERITY.get(symptom, 1) for symptom in input_symptoms)
    
    for disease, symptoms in DISEASE_SYMPTOM_MAP.items():
        # Find the symptoms that match between input and disease
        matching = set(input_symptoms) & set(symptoms)
        
        if matching:
            # Calculate weighted score based on symptom severity
            severity_score = sum(SYMPTOM_SEVERITY.get(symptom, 1) for symptom in matching)
            
            # Calculate coverage score (what percentage of disease symptoms are matched)
            coverage = len(matching) / len(symptoms) if len(symptoms) > 0 else 0
            
            # Calculate input coverage (what percentage of input symptoms are matched)
            input_coverage = len(matching) / len(input_symptoms) if len(input_symptoms) > 0 else 0
            
            # Calculate severity coverage (what percentage of total severity is matched)
            disease_severity_total = sum(SYMPTOM_SEVERITY.get(symptom, 1) for symptom in symptoms)
            severity_coverage = severity_score / disease_severity_total if disease_severity_total > 0 else 0
            
            # Calculate final score (weighted combination of different metrics)
            final_score = (0.4 * coverage) + (0.3 * input_coverage) + (0.3 * severity_coverage)
            
            if final_score > max_score:
                max_score = final_score
                predicted_disease = disease
                matched_symptoms = {symptom: SYMPTOM_SEVERITY.get(symptom, 1) for symptom in matching}
    
    # If no disease found in dataset.csv, fall back to the original map
    if predicted_disease == "Unknown":
        return predict_with_pattern_matching(input_symptoms)
    
    # Calculate confidence (convert score to percentage)
    confidence = min(max_score * 100, 100)  # Cap at 100%
    
    result = {
        "disease": predicted_disease,
        "confidence": confidence,
        "matched_symptoms": len(matched_symptoms)
    }
    
    # Add description and precautions if available
    if predicted_disease in DISEASE_DESCRIPTIONS:
        result["description"] = DISEASE_DESCRIPTIONS[predicted_disease]
    
    if predicted_disease in DISEASE_PRECAUTIONS:
        result["precautions"] = DISEASE_PRECAUTIONS[predicted_disease]
        
    return result


def predict_with_pattern_matching(input_symptoms):
    """Simple pattern matching algorithm for disease prediction using fallback data"""
    max_match = 0
    predicted_disease = "Unknown"
    
    for disease, symptoms in FALLBACK_DISEASE_MAP.items():
        matches = len(set(input_symptoms) & set(symptoms))
        if matches > max_match:
            max_match = matches
            predicted_disease = disease
    
    # Calculate confidence based on the number of matched symptoms
    if predicted_disease != "Unknown":
        total_symptoms = len(FALLBACK_DISEASE_MAP.get(predicted_disease, []))
        confidence = (max_match / total_symptoms) * 100 if total_symptoms > 0 else 0
    else:
        confidence = 0
    
    result = {
        "disease": predicted_disease,
        "confidence": confidence
    }
    
    # Add description and precautions if available
    if predicted_disease in DISEASE_DESCRIPTIONS:
        result["description"] = DISEASE_DESCRIPTIONS[predicted_disease]
    elif predicted_disease in FALLBACK_DESCRIPTIONS:
        result["description"] = FALLBACK_DESCRIPTIONS[predicted_disease]
    
    if predicted_disease in DISEASE_PRECAUTIONS:
        result["precautions"] = DISEASE_PRECAUTIONS[predicted_disease]
    elif predicted_disease in FALLBACK_PRECAUTIONS:
        result["precautions"] = FALLBACK_PRECAUTIONS[predicted_disease]
        
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-symptoms':
            print(json.dumps(get_all_symptoms()))
        else:
            try:
                symptoms = json.loads(sys.argv[1])
                result = predict(symptoms)
                print(json.dumps(result))
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid symptoms format"}))
    else:
        print(json.dumps({"error": "No arguments provided"})) 