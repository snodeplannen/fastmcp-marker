"""
Test script voor Gradio API met verschillende opties om ZIP downloads te testen.
"""

from gradio_client import Client, handle_file  # type: ignore
import os

def test_gradio_api_zip() -> bool:
    """Test de Gradio API voor ZIP downloads met verschillende opties."""
    
    print("🧪 Testing Gradio API for ZIP downloads with different options...")
    
    # Maak client
    client = Client("http://127.0.0.1:7860/")
    
    # Test PDF pad
    test_pdf_path = "testdocument2.pdf"
    
    if not os.path.exists(test_pdf_path):
        print("❌ Test PDF not found!")
        return False
    
    print(f"📄 Using test PDF: {test_pdf_path}")
    
    # Test verschillende configuraties
    test_configs = [
        {
            "name": "Basic (no images, no debug)",
            "extract_images": False,
            "debug_layout_images": False,
            "debug_pdf_images": False,
            "debug_json": False,
            "include_images_in_zip": False,
            "include_debug_in_zip": False,
            "expected_files": ["00_OVERVIEW.md", "01_testdocument2/converted_text.md"]
        },
        {
            "name": "With Images Only",
            "extract_images": True,
            "debug_layout_images": False,
            "debug_pdf_images": False,
            "debug_json": False,
            "include_images_in_zip": True,
            "include_debug_in_zip": False,
            "expected_files": ["00_OVERVIEW.md", "01_testdocument2/converted_text.md", "01_testdocument2/images/"]
        },
        {
            "name": "With Debug Images Only",
            "extract_images": False,
            "debug_layout_images": True,
            "debug_pdf_images": False,
            "debug_json": False,
            "include_images_in_zip": False,
            "include_debug_in_zip": True,
            "expected_files": ["00_OVERVIEW.md", "01_testdocument2/converted_text.md", "01_testdocument2/output/debug_data/"]
        },
        {
            "name": "Full Debug Mode",
            "extract_images": True,
            "debug_layout_images": True,
            "debug_pdf_images": True,
            "debug_json": True,
            "include_images_in_zip": True,
            "include_debug_in_zip": True,
            "expected_files": ["00_OVERVIEW.md", "01_testdocument2/converted_text.md", "01_testdocument2/images/", "01_testdocument2/output/debug_data/"]
        }
    ]
    
    all_tests_passed = True
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n🧪 Test {i}/4: {config['name']}")
        print(f"   📋 Config: extract_images={config['extract_images']}, debug_layout_images={config['debug_layout_images']}, debug_pdf_images={config['debug_pdf_images']}, debug_json={config['debug_json']}")
        
        try:
            # Test de API call met de juiste parameters
            result = client.predict(
                uploaded_files=[handle_file(test_pdf_path)],
                progress="markdown",
                param_2="",  # Pagina Bereik
                param_3=False,  # Debug Modus
                param_4="",  # Output Directory
                param_5=False,  # Forceer OCR
                param_6=False,  # Strip Bestaande OCR
                param_7=False,  # Schakel OCR Uit
                param_8="",  # Talen voor OCR
                param_9=0.7,  # OCR Space Threshold
                param_10=0.6,  # OCR Newline Threshold
                param_11=0.3,  # OCR Alphanumeric Threshold
                param_12=False,  # Gebruik LLM
                param_13="ollama",  # LLM Provider
                param_14="",  # Google API Key
                param_15="gemini-2.0-flash",  # Gemini Model
                param_16="",  # OpenAI API Key
                param_17="gpt-4o",  # OpenAI Model
                param_18="",  # OpenAI Base URL
                param_19="",  # Anthropic API Key
                param_20="claude-3-5-sonnet-20241022",  # Anthropic Model
                param_21="",  # Azure API Key
                param_22="",  # Azure Endpoint
                param_23="",  # Azure Deployment
                param_24="2024-02-15-preview",  # Azure API Version
                param_25="http://localhost:11434",  # Ollama Base URL
                param_26="llama3.2:latest",  # Ollama Model
                param_27="",  # Custom API Key
                param_28="",  # Custom Base URL
                param_29="",  # Custom Model
                param_30=3,  # Max Retries
                param_31=3,  # Max Concurrency
                param_32=60,  # Timeout
                param_33=0.1,  # Temperature
                param_34=4096,  # Max Tokens
                param_35=False,  # LLM Layout Builder
                param_36=False,  # LLM Table Processor
                param_37=False,  # LLM Equation Processor
                param_38=False,  # LLM Handwriting Processor
                param_39=False,  # LLM Complex Region Processor
                param_40=False,  # LLM Form Processor
                param_41=False,  # LLM Image Description
                param_42=False,  # LLM Table Merge
                param_43=False,  # LLM Text Processor
                param_44="",  # Layout Prompt
                param_45="",  # Table Prompt
                param_46="",  # Equation Prompt
                param_47="",  # Handwriting Prompt
                param_48="",  # Complex Relabeling Prompt
                param_49="",  # Table Rewriting Prompt
                param_50="",  # Table Merge Prompt
                param_51="",  # Image Description Prompt
                param_52=0.7,  # Confidence Threshold
                param_53=0.8,  # Picture Height Threshold
                param_54=0.08,  # Min Equation Height
                param_55=0.05,  # Equation Image Expansion Ratio
                param_56=60,  # Max Rows Per Batch
                param_57=0,  # Table Image Expansion Ratio
                param_58=0.6,  # Table Height Threshold
                param_59=0.2,  # Table Start Threshold
                param_60=0.25,  # Vertical Table Height Threshold
                param_61=20,  # Vertical Table Distance Threshold
                param_62=0.25,  # Horizontal Table Width Threshold
                param_63=20,  # Horizontal Table Distance Threshold
                param_64=50,  # Column Gap Threshold
                param_65=0.01,  # Image Expansion Ratio
                param_66=96,  # Low-res Image DPI
                param_67=192,  # High-res Image DPI
                param_68=0.1,  # Layout Coverage Threshold
                param_69=0.8,  # Document OCR Threshold
                param_70=False,  # Detecteer Boxes
                param_71=175,  # Max Tabel Rijen
                param_72=0.5,  # Row Split Threshold
                param_73=0.02,  # Column Gap Ratio
                param_74=1,  # PDFText Workers (ALTIJD 1)
                param_75=0,  # Batch Size
                param_76=0,  # Recognition Batch Size
                param_77=0,  # Detection Batch Size
                param_78=config["extract_images"],  # Extraheer Afbeeldingen
                param_79=False,  # Pagina Output
                param_80="------------------------------------------------",  # Pagina Separator
                param_81=False,  # Schakel Links Uit
                param_82=config["include_images_in_zip"],  # Inclusief Afbeeldingen in ZIP
                param_83=config["include_debug_in_zip"],  # Inclusief Debug Bestanden in ZIP
                param_84=config["debug_layout_images"],  # Debug Layout Images
                param_85=config["debug_pdf_images"],  # Debug PDF Images
                param_86=config["debug_json"],  # Debug JSON
                param_87="debug_data",  # Debug Data Folder
                api_name="/process_pdf"
            )
            
            print("✅ API call successful!")
            
            # Controleer de resultaten
            if len(result) >= 4:
                zip_path_dict = result[2]
                error_details = result[3]
                
                if error_details and error_details.strip():
                    print(f"❌ Error details: {error_details}")
                    all_tests_passed = False
                    continue
                else:
                    print("✅ No errors")
                
                # Extraheer het echte ZIP pad uit de dictionary
                if isinstance(zip_path_dict, dict) and 'value' in zip_path_dict:
                    zip_path = zip_path_dict['value']
                else:
                    zip_path = zip_path_dict
                
                # Controleer of er een ZIP bestand is
                if zip_path and zip_path != "":
                    print(f"📦 ZIP file created: {zip_path}")
                    
                    # Controleer ZIP inhoud
                    if os.path.exists(zip_path):
                        import zipfile
                        import tempfile
                        import shutil
                        
                        print("📦 ZIP file exists, downloading and extracting...")
                        
                        # Download en extract de ZIP
                        with zipfile.ZipFile(zip_path, 'r') as z:
                            files_in_zip = z.namelist()
                            print(f"📁 ZIP contains {len(files_in_zip)} files:")
                            
                            # Extract naar een tijdelijke directory
                            extract_dir = tempfile.mkdtemp(prefix="zip_test_")
                            z.extractall(extract_dir)
                            
                            print(f"📂 Extracted to: {extract_dir}")
                            
                            # Valideer verwachte bestanden
                            print("\n🔍 Validating expected files:")
                            test_passed = True
                            
                            # Check if expected_files exists and is iterable
                            expected_files = config.get("expected_files", [])
                            if not isinstance(expected_files, (list, tuple)):
                                print(f"  ⚠️ Warning: expected_files is not a list, got {type(expected_files)}")
                                expected_files = []
                            
                            for expected_file in expected_files:
                                found = False
                                for file in files_in_zip:
                                    if expected_file in file:
                                        found = True
                                        break
                                
                                if found:
                                    print(f"  ✅ {expected_file} - Found")
                                else:
                                    print(f"  ❌ {expected_file} - Missing")
                                    test_passed = False
                            
                            # Analyseer de inhoud
                            print("\n📋 ZIP Content Analysis:")
                            for file in files_in_zip:
                                file_path = os.path.join(extract_dir, file)
                                if os.path.isfile(file_path):
                                    file_size = os.path.getsize(file_path)
                                    print(f"  📄 {file} ({file_size} bytes)")
                                    
                                    # Toon inhoud van belangrijke bestanden
                                    if file.endswith('.md') and 'OVERVIEW' in file:
                                        print("    📝 Overview content:")
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            content = f.read()
                                            lines = content.split('\n')[:5]  # Eerste 5 regels
                                            for line in lines:
                                                if line.strip():
                                                    print(f"      {line}")
                                    
                                    elif file.endswith('.png'):
                                        print("    🖼️ Image file detected")
                                
                                elif os.path.isdir(file_path):
                                    print(f"  📁 {file}/ (directory)")
                            
                            # Cleanup
                            shutil.rmtree(extract_dir)
                            print("🧹 Cleaned up temporary directory")
                        
                        if test_passed:
                            print(f"✅ Test {i} PASSED")
                        else:
                            print(f"❌ Test {i} FAILED")
                            all_tests_passed = False
                    else:
                        print("❌ ZIP file does not exist!")
                        all_tests_passed = False
                else:
                    print("❌ No ZIP file path in response!")
                    all_tests_passed = False
                    
            else:
                print("❌ Invalid response format!")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
            all_tests_passed = False
    
    return all_tests_passed

if __name__ == "__main__":
    success = test_gradio_api_zip()
    
    if success:
        print("\n🎉 All API tests passed! ZIP downloads work with all configurations!")
    else:
        print("\n❌ Some API tests failed!")
