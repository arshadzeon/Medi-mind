'use client';

import { useState, useEffect } from 'react';
import { SignedIn } from '@clerk/nextjs';

interface PredictionResult {
  disease: string;
  confidence: number;
  description?: string;
  precautions?: string[];
  error?: string;
}

export default function DiseasePredictor() {
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoadingSymptoms, setIsLoadingSymptoms] = useState(true);

  useEffect(() => {
    const fetchSymptoms = async () => {
      setIsLoadingSymptoms(true);
      try {
        console.log('Fetching symptoms...');
        const response = await fetch('/api/prediction');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to fetch symptoms');
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        
        if (data.symptoms && Array.isArray(data.symptoms) && data.symptoms.length > 0) {
          console.log(`Successfully loaded ${data.symptoms.length} symptoms`);
          setSymptoms(data.symptoms);
        } else {
          console.error('No symptoms in response:', data);
          throw new Error('No symptoms received');
        }
      } catch (err: any) {
        console.error('Error fetching symptoms:', err);
        setError(`Failed to load symptoms: ${err.message || 'Unknown error'}`);
        
        // Fallback symptoms in case the API fails
        setSymptoms([
          "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering",
          "chills", "joint_pain", "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting",
          "burning_micturition", "fatigue", "weight_loss", "cough", "high_fever",
          "breathlessness", "sweating", "headache", "yellowish_skin", "dark_urine"
        ]);
      } finally {
        setIsLoadingSymptoms(false);
      }
    };

    fetchSymptoms();
  }, []);

  const handleSymptomToggle = (symptom: string) => {
    setSelectedSymptoms(prev =>
      prev.includes(symptom)
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom]
    );
  };

  const handlePredict = async () => {
    if (selectedSymptoms.length === 0) {
      setError('Please select at least one symptom');
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      console.log('Sending prediction request with symptoms:', selectedSymptoms);
      const response = await fetch('/api/prediction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symptoms: selectedSymptoms }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get prediction');
      }

      const data = await response.json();
      console.log('Prediction result:', data);
      
      // Don't throw an error if there's an error property, just display it in the UI
      setPrediction(data);
    } catch (err: any) {
      console.error('Prediction error:', err);
      setError(`Failed to get prediction: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const filteredSymptoms = symptoms.filter(symptom =>
    symptom.toLowerCase().replace(/_/g, ' ').includes(searchTerm.toLowerCase())
  );

  const formatName = (name: string) => {
    return name
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <SignedIn>
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="py-12 md:py-20">
          <div className="max-w-3xl mx-auto text-center pb-12 md:pb-20">
            <h2 className="h2 mb-4">Disease Predictor</h2>
            <p className="text-xl text-gray-400">Select your symptoms to get a prediction</p>
          </div>

          <div className="max-w-xl mx-auto">
            {error && (
              <div className="mb-4 p-4 bg-red-500/10 border border-red-500 rounded-lg text-red-500">
                {error}
              </div>
            )}

            <div className="mb-6">
              <div className="mb-4">
                <input
                  type="text"
                  placeholder="Search symptoms..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full p-2 rounded-lg bg-gray-800 text-gray-200 border border-gray-700 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2">Selected Symptoms:</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedSymptoms.length === 0 ? (
                    <p className="text-gray-500 italic">No symptoms selected</p>
                  ) : (
                    selectedSymptoms.map((symptom) => (
                      <span
                        key={symptom}
                        className="px-3 py-1 bg-indigo-600 text-white rounded-full text-sm flex items-center gap-2"
                      >
                        {formatName(symptom)}
                        <button
                          onClick={() => handleSymptomToggle(symptom)}
                          className="text-white hover:text-red-300"
                        >
                          ×
                        </button>
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div className="max-h-60 overflow-y-auto rounded-lg border border-gray-700">
                <div className="grid grid-cols-1 gap-1 p-2">
                  {isLoadingSymptoms ? (
                    <div className="p-4 text-center">
                      <p className="text-gray-400">Loading symptoms...</p>
                    </div>
                  ) : filteredSymptoms.length > 0 ? (
                    filteredSymptoms.map((symptom) => (
                      <button
                        key={symptom}
                        onClick={() => handleSymptomToggle(symptom)}
                        className={`p-2 text-left rounded transition-colors ${
                          selectedSymptoms.includes(symptom)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                      >
                        {formatName(symptom)}
                      </button>
                    ))
                  ) : searchTerm ? (
                    <p className="p-2 text-gray-500 italic">No symptoms found for "{searchTerm}"</p>
                  ) : (
                    <p className="p-2 text-gray-500 italic">No symptoms available</p>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={handlePredict}
              disabled={loading || selectedSymptoms.length === 0}
              className="btn w-full bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing Symptoms...' : 'Get Prediction'}
            </button>

            {prediction && (
              <div className="mt-6 p-6 bg-gray-800 rounded-lg">
                <h3 className="text-xl mb-4 font-bold">Prediction Result</h3>
                
                {prediction.error ? (
                  <div className="text-red-400 mb-4">
                    <p>Error: {prediction.error}</p>
                  </div>
                ) : (
                  <>
                    <div className="mb-4">
                      <h4 className="text-lg text-indigo-400 mb-1">Disease:</h4>
                      <p className="text-xl font-semibold text-white">{formatName(prediction.disease)}</p>
                    </div>
                    
                    <div className="mb-4">
                      <h4 className="text-lg text-indigo-400 mb-1">Confidence:</h4>
                      <div className="w-full bg-gray-700 rounded-full h-4">
                        <div 
                          className="bg-indigo-600 h-4 rounded-full" 
                          style={{ width: `${Math.min(100, prediction.confidence)}%` }}
                        />
                      </div>
                      <p className="mt-1 text-white">{prediction.confidence.toFixed(2)}%</p>
                    </div>
                  </>
                )}
                
                {prediction.description && (
                  <div className="mb-4">
                    <h4 className="text-lg text-indigo-400 mb-1">Description:</h4>
                    <p className="text-gray-200">{prediction.description}</p>
                  </div>
                )}
                
                {prediction.precautions && prediction.precautions.length > 0 && (
                  <div>
                    <h4 className="text-lg text-indigo-400 mb-1">Precautions:</h4>
                    <ul className="list-disc pl-5 text-gray-200">
                      {prediction.precautions.map((precaution, index) => (
                        <li key={index}>{precaution}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </SignedIn>
  );
} 