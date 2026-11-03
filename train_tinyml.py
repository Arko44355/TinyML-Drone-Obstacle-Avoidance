import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import classification_report, accuracy_score
import joblib

# 1. Load Dataset
df = pd.read_csv('drone_sensor_dataset.csv')
X = df.drop(columns=['action'])
y = df['action']

# 2. Split Dataset (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Ultra-Lightweight Decision Tree Model (TinyML Friendly)
clf = DecisionTreeClassifier(max_depth=5, random_state=42)
clf.fit(X_train, y_train)

# 4. Evaluate Model Performance
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"=== Model Evaluation ===")
print(f"Accuracy: {acc * 100:.2f}%\n")
print(classification_report(y_test, y_pred, target_names=['Move Straight', 'Turn Left', 'Turn Right']))

# 5. Convert Decision Tree directly into C Code for STM32/ESP32
def tree_to_c(decision_tree, feature_names):
    tree = decision_tree.tree_
    c_code = "// Auto-generated TinyML Decision Tree Model for Microcontrollers\n"
    c_code += "// Inputs: float sensor[5] -> [left90, left45, front, right45, right90]\n"
    c_code += "// Output: int (0: Straight, 1: Left, 2: Right)\n\n"
    c_code += "int predict_drone_action(const float* sensor) {\n"

    def recurse(node, depth):
        indent = "    " * depth
        if tree.feature[node] != -2:
            name = feature_names[tree.feature[node]]
            threshold = tree.threshold[node]
            
            # Mapping feature names to sensor index
            sensor_map = {
                'sensor_left90': 'sensor[0]',
                'sensor_left45': 'sensor[1]',
                'sensor_front': 'sensor[2]',
                'sensor_right45': 'sensor[3]',
                'sensor_right90': 'sensor[4]'
            }
            s_name = sensor_map[name]
            
            return f"{indent}if ({s_name} <= {threshold:.4f}f) {{\n" + \
                   recurse(tree.children_left[node], depth + 1) + \
                   f"{indent}}} else {{\n" + \
                   recurse(tree.children_right[node], depth + 1) + \
                   f"{indent}}}\n"
        else:
            value = tree.value[node][0]
            class_id = np.argmax(value)
            return f"{indent}return {class_id};\n"

    c_code += recurse(0, 1)
    c_code += "}\n"
    return c_code

# Save C Header File
c_model = tree_to_c(clf, X.columns.tolist())
with open("tinyml_model.h", "w") as f:
    f.write(c_model)

print("Success! Trained TinyML model and exported 'tinyml_model.h' C-header file for Microcontroller!")
