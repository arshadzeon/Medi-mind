import DiseasePredictor from '@/components/disease-predictor';

export const metadata = {
  title: 'Disease Predictor',
  description: 'Predict diseases based on symptoms using machine learning',
};

export default function PredictPage() {
  return <DiseasePredictor />;
} 