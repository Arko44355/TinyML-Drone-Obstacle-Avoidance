// Auto-generated TinyML Decision Tree Model for Microcontrollers
// Inputs: float sensor[5] -> [left90, left45, front, right45, right90]
// Output: int (0: Straight, 1: Left, 2: Right)

int predict_drone_action(const float* sensor) {
    if (sensor[1] <= 0.8008f) {
        if (sensor[4] <= 0.3179f) {
            if (sensor[2] <= 1.0440f) {
                return 1;
            } else {
                return 2;
            }
        } else {
            if (sensor[2] <= 0.9359f) {
                if (sensor[3] <= 0.5105f) {
                    if (sensor[1] <= 0.5004f) {
                        return 2;
                    } else {
                        return 1;
                    }
                } else {
                    if (sensor[4] <= 0.6982f) {
                        return 2;
                    } else {
                        return 2;
                    }
                }
            } else {
                return 2;
            }
        }
    } else {
        if (sensor[3] <= 0.8010f) {
            if (sensor[0] <= 0.5803f) {
                if (sensor[2] <= 0.3820f) {
                    return 2;
                } else {
                    if (sensor[2] <= 0.7571f) {
                        return 1;
                    } else {
                        return 1;
                    }
                }
            } else {
                return 1;
            }
        } else {
            if (sensor[2] <= 1.0007f) {
                if (sensor[0] <= 2.3485f) {
                    if (sensor[4] <= 0.8037f) {
                        return 1;
                    } else {
                        return 2;
                    }
                } else {
                    if (sensor[1] <= 2.0583f) {
                        return 2;
                    } else {
                        return 1;
                    }
                }
            } else {
                return 0;
            }
        }
    }
}
