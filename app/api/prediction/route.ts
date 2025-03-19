import { NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';

interface PredictionResult {
  disease: string;
  confidence: number;
}

const execPromise = promisify(exec);
// Try different Python executable names in order
const pythonExecutables = ['python3', 'python', 'py'];

async function findPythonExecutable(): Promise<string> {
  for (const pythonExec of pythonExecutables) {
    try {
      await execPromise(`${pythonExec} --version`);
      return pythonExec;
    } catch (error) {
      continue;
    }
  }
  return 'python3'; // Default to python3 if no executable found
}

// List all files in a directory for debugging purposes
async function listDirContents(dir: string): Promise<string[]> {
  try {
    return fs.readdirSync(dir);
  } catch (e) {
    return [`Error reading directory ${dir}: ${e}`];
  }
}

export async function GET() {
  try {
    const pythonExec = await findPythonExecutable();
    console.log(`Using Python executable: ${pythonExec}`);

    // Check if data directory exists
    const dataDir = path.join(process.cwd(), 'public/data');
    if (!fs.existsSync(dataDir)) {
      console.error(`Data directory doesn't exist: ${dataDir}`);
      return NextResponse.json({
        error: 'Data directory not found',
        path: dataDir,
        debug: { 
          cwd: process.cwd(),
          files: await listDirContents(process.cwd())
        }
      }, { status: 500 });
    }

    // List files in the data directory for debugging
    const dataFiles = await listDirContents(dataDir);
    console.log(`Files in data directory: ${JSON.stringify(dataFiles)}`);
    
    if (!dataFiles.includes('Training.csv')) {
      console.error(`Training.csv not found in data directory: ${dataDir}`);
      return NextResponse.json({
        error: 'Training.csv not found',
        dataFiles,
      }, { status: 500 });
    }

    // Create a temporary file with the Python script
    const tempFile = path.join(os.tmpdir(), 'symptoms-script.py');
    const pythonCode = `
import sys
import os
import json

# Print environment for debugging
print("PYTHON DEBUG INFO:", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {os.getcwd()}", file=sys.stderr)
print(f"Data path: {os.path.join(os.getcwd(), 'public/data')}", file=sys.stderr)
data_files = os.listdir(os.path.join(os.getcwd(), 'public/data'))
print(f"Data files: {data_files}", file=sys.stderr)

sys.path.append('${path.join(process.cwd(), 'lib/ml')}')
try:
    import disease_predictor
    symptoms = disease_predictor.get_all_symptoms()
    print(json.dumps(symptoms))
except Exception as e:
    print(f"Error importing or running disease_predictor: {str(e)}", file=sys.stderr)
    # Provide a fallback set of symptoms
    fallback_symptoms = [
        "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering",
        "chills", "joint_pain", "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting",
        "burning_micturition", "fatigue", "weight_loss", "cough", "high_fever",
        "breathlessness", "sweating", "headache", "yellowish_skin", "dark_urine",
        "nausea", "loss_of_appetite", "abdominal_pain", "diarrhoea", "mild_fever",
        "yellowing_of_eyes", "swelled_lymph_nodes", "malaise", "blurred_vision"
    ]
    print(json.dumps(fallback_symptoms))
    `;
    
    fs.writeFileSync(tempFile, pythonCode);
    console.log(`Created temp file at: ${tempFile}`);

    try {
      console.log(`Executing Python script: ${pythonExec} ${tempFile}`);
      const { stdout, stderr } = await execPromise(`${pythonExec} ${tempFile}`);
      
      if (stderr) {
        console.error(`Python stderr: ${stderr}`);
      }
      
      console.log(`Python stdout length: ${stdout.length}`);
      if (stdout.trim().length === 0) {
        console.error('Python script returned empty output');
        return NextResponse.json({
          error: 'No output from Python script',
          debug: { stderr }
        }, { status: 500 });
      }
      
      let symptoms;
      try {
        symptoms = JSON.parse(stdout.trim());
      } catch (parseError) {
        console.error(`Failed to parse JSON from stdout: ${stdout}`);
        return NextResponse.json({
          error: 'Failed to parse symptoms JSON',
          debug: { stdout, stderr }
        }, { status: 500 });
      }
      
      if (!Array.isArray(symptoms) || symptoms.length === 0) {
        console.error(`Invalid symptoms data returned: ${JSON.stringify(symptoms)}`);
        return NextResponse.json({
          error: 'Invalid symptoms data returned',
          debug: { symptoms, stderr }
        }, { status: 500 });
      }
      
      console.log(`Successfully got ${symptoms.length} symptoms`);
      return NextResponse.json({ symptoms });
    } catch (error: any) {
      console.error('Python execution error:', error);
      return NextResponse.json({
        error: 'Failed to fetch symptoms',
        message: error.message,
        debug: { cmd: `${pythonExec} ${tempFile}` }
      }, { status: 500 });
    } finally {
      // Clean up temp file
      try {
        fs.unlinkSync(tempFile);
      } catch (e) {
        console.error('Failed to delete temp file:', e);
      }
    }
  } catch (error: any) {
    console.error('Error fetching symptoms:', error);
    return NextResponse.json({
      error: 'Failed to fetch symptoms',
      message: error.message
    }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { symptoms } = await req.json();

    if (!symptoms || !Array.isArray(symptoms)) {
      return NextResponse.json(
        { error: 'Invalid symptoms format' },
        { status: 400 }
      );
    }

    const pythonExec = await findPythonExecutable();

    // Create a temporary file with the Python script
    const tempFile = path.join(os.tmpdir(), 'prediction-script.py');
    const pythonCode = `
import sys
import os
import json

# Print environment for debugging
print("PYTHON DEBUG INFO:", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {os.getcwd()}", file=sys.stderr)

sys.path.append('${path.join(process.cwd(), 'lib/ml')}')
try:
    import disease_predictor
    symptoms = json.loads('${JSON.stringify(symptoms)}')
    result = disease_predictor.predict(symptoms)
    print(json.dumps(result))
except Exception as e:
    print(f"Error predicting disease: {str(e)}", file=sys.stderr)
    # Provide a fallback prediction
    print(json.dumps({
        "disease": "Unknown",
        "confidence": 0,
        "error": str(e)
    }))
    `;
    
    fs.writeFileSync(tempFile, pythonCode);

    try {
      const { stdout, stderr } = await execPromise(`${pythonExec} ${tempFile}`);
      
      if (stderr) {
        console.error(`Python stderr: ${stderr}`);
      }
      
      const result = JSON.parse(stdout.trim());
      
      if (result.error) {
        console.error(`Python error: ${result.error}`);
      }
      
      return NextResponse.json(result);
    } catch (error: any) {
      console.error('Python execution error:', error);
      return NextResponse.json({
        error: 'Failed to process prediction',
        message: error.message
      }, { status: 500 });
    } finally {
      // Clean up temp file
      try {
        fs.unlinkSync(tempFile);
      } catch (e) {
        console.error('Failed to delete temp file:', e);
      }
    }
  } catch (error: any) {
    console.error('Prediction error:', error);
    return NextResponse.json({
      error: 'Failed to process prediction',
      message: error.message
    }, { status: 500 });
  }
} 