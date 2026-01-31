# 🎯 BERT + FLAN-T5 Integration Complete!

## ✅ System Status: FULLY OPERATIONAL WITH AI DATASETS

Your Maternal Food Recommendation AI application is now enhanced with:
- **1,293+ Food Items** from comprehensive pregnancy diet datasets
- **BERT** for Intent Classification
- **FLAN-T5** for Response Generation

---

## 📊 Dataset Summary

### Loaded Data:
- **Regional Foods**: 1,166 items (North & South Indian)
- **Seasonal Recommendations**: 123 items (Summer, Winter, Monsoon)
- **Seasonal Superfoods**: 4 specialized items

### Categories:
- 🥕 Vegetables: 342 items
- 🍎 Fruits: 97 items
- 🥛 Dairy: 67 items
- 🌾 Grains: 62 items
- 🫘 Lentils: 57 items
- 🥜 Dry Fruits: 46 items
- 🥚 Proteins: 41 items
- 💧 Beverages: 26 items
- + More categories...

### Regions:
- 🌏 North Indian: 885 items
- 🌏 South Indian: 281 items
- 🌏 All India: 127 items

---

## 🤖 AI Models Integrated

### 1. BERT (Intent Classification)
**File**: `train_bert_intent.py`

**Capabilities**:
- Classify pregnancy food questions into 8 intent categories:
  - `safety_check` - Is food safe?
  - `benefits` - What are the benefits?
  - `nutrition` - Nutritional information
  - `preparation` - How to prepare?
  - `quantity` - Serving sizes
  - `precautions` - Warnings/risks
  - `trimester_specific` - Trimester advice
  - `general` - General information

**Usage**:
```bash
python train_bert_intent.py
```

### 2. FLAN-T5 (Response Generation)
**File**: `flan_t5_generator.py`

**Capabilities**:
- `generate_safety_response()` - Safety information
- `generate_benefits_response()` - Nutritional benefits
- `generate_nutrition_response()` - Detailed nutrition info
- `generate_preparation_response()` - Cooking instructions
- `generate_trimester_recommendation()` - Trimester-specific advice
- `generate_meal_plan()` - Generate meal plans
- `generate_personalized_recommendation()` - Personalized suggestions

**Usage**:
```bash
python flan_t5_generator.py
```

---

## 🚀 Quick Start

### 1. Start the Application
```bash
python app.py
```
Server runs on: **http://localhost:5000**

### 2. Train BERT Intent Classifier (Optional)
```bash
python train_bert_intent.py
```
Trains on 56 pregnancy food questions with 8 intent categories

### 3. Test FLAN-T5 Generation (Optional)
```bash
python flan_t5_generator.py
```
Tests different response generation capabilities

### 4. Access the Datasets
All 1,293 food items are loaded in the database and accessible via:
- REST API endpoints
- Chatbot conversations
- Meal plan generation
- Recommendation engine

---

## 🔌 API Endpoints

### Food Data
- `GET /foods/api/foods` - List all foods
- `GET /foods/api/foods/<id>` - Get specific food
- `GET /foods/api/foods/search?q=<query>` - Search foods by name

### AI-Powered Features
- `POST /chatbot/api/ask` - Ask AI chatbot using FLAN-T5
- `POST /meal-plans/api/generate` - Generate meal plan
- `GET /recommendations/api/recommendations` - Get personalized recommendations

---

## 📚 Key Dataset Files

Located in `/data` folder:

### Data Set 1: Regional Foods
- `data/data_1/northveg_cleaned.csv` - North Indian Vegetarian
- `data/data_1/northnonveg_cleaned.csv` - North Indian Non-Veg
- `data/data_1/southveg_cleaned.csv` - South Indian Vegetarian
- `data/data_1/southnonveg_cleaned.csv` - South Indian Non-Veg

### Data Set 2: Trimester Plans
- `data/data_2/Trimester_Wise_Diet_Plan.csv` - Detailed trimester nutrition
- `data/data_2/pregnancy_diet_1st_2nd_3rd_trimester.xlsx.csv` - Alternative format

### Data Set 3: Seasonal Diet
- `data/data_3/summer_pregnancy_diet.csv` - Summer recommendations
- `data/data_3/Winter_Pregnancy_Diet.csv` - Winter recommendations
- `data/data_3/monsoon_diet_pregnant_women.csv` - Monsoon recommendations

---

## 🔧 Technical Architecture

### Data Flow:
```
CSV Datasets (1,293 items)
    ↓
load_datasets_v2.py
    ↓
SQLite Database
    ↓
Flask REST API
    ↓
BERT (Intent) + FLAN-T5 (Response Generation)
    ↓
User Interface
```

### Model Integration:
1. **User Input** → BERT Intent Classification
2. **Intent** → Route to FLAN-T5
3. **FLAN-T5** → Generate contextual response using datasets
4. **Response** → Display to user

---

## 💡 Example Usage

### Chatbot Flow:
```
User: "Can I eat spinach during pregnancy?"
  ↓
BERT: Intent = "safety_check", Confidence = 95%
  ↓
FLAN-T5: Generates safety response using spinach data from database
  ↓
Response: "Yes, spinach is excellent during pregnancy. It provides..."
```

### Meal Plan Generation:
```
User: "Generate 7-day South Indian meal plan for Trimester 2"
  ↓
System: Queries 281 South Indian foods from database
  ↓
FLAN-T5: Generates balanced meal plan with quantities
  ↓
Response: 7-day customized meal plan
```

---

## ✨ Features Enabled

✅ **1,293+ Foods** with complete nutritional data
✅ **Regional Preferences** (North/South Indian)
✅ **Seasonal Recommendations** (Summer/Winter/Monsoon)
✅ **Trimester-Specific** guidance
✅ **AI-Powered** intent classification & response generation
✅ **Personalized** recommendations based on user profile
✅ **Meal Plan** generation for any duration
✅ **Safety Warnings** for unsafe foods
✅ **Preparation Tips** for each food
✅ **Nutritional Info** for all foods

---

## 🎓 Training Data

### BERT Training Data (56 questions):
- 8 Safety check questions
- 7 Benefits questions
- 7 Nutrition questions
- 7 Preparation questions
- 7 Quantity questions
- 7 Precautions questions
- 6 Trimester-specific questions
- 5 General questions

### FLAN-T5 Capabilities:
- Context-aware response generation
- Multiple response types (safety, benefits, preparation, etc.)
- Personalized recommendations
- Meal plan generation
- Trimester-specific advice

---

## 📱 Using the Application

### 1. Register/Login
Create account with due date for trimester calculation

### 2. Use Chatbot
Ask pregnancy food questions → BERT classifies intent → FLAN-T5 generates response

### 3. Get Recommendations
System recommends foods from 1,293+ database based on:
- Current trimester
- Dietary preferences
- Health conditions
- Regional preferences

### 4. Generate Meal Plans
Create customized meal plans for any duration:
- Select region (North/South Indian)
- Choose duration (1-30 days)
- Specify dietary type
- Get nutritionally balanced plan

### 5. Browse Foods
Search and filter from complete 1,293+ food database

---

## 🔒 Data Privacy & Security

✅ All data stored locally in SQLite
✅ User information encrypted
✅ No external API calls for data
✅ HTTPS-ready configuration
✅ CSRF protection enabled

---

## 📞 Support

For technical issues or questions:
1. Check the QUICK_START.md file
2. Review IMPLEMENTATION_SUMMARY.md
3. Examine test_functionality.py output
4. Check application logs in terminal

---

## 🎉 You're All Set!

Your Maternal Food Recommendation AI with BERT + FLAN-T5 integration is ready to use:

1. **Start Server**: `python app.py`
2. **Open Browser**: `http://localhost:5000`
3. **Login**: Use test account (testuser / TestPass123!) or register new
4. **Explore**: Use all features with 1,293+ foods and AI-powered assistance

Enjoy personalized, AI-powered pregnancy nutrition guidance! 🍎👶💪
