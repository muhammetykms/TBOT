def evaluate_conditions(parameters, data):
    def evaluate_condition(condition, data):
        # Tek koşulları değerlendir
        for key, value in condition.items():
            if key == "logic":  # Mantıksal operatör
                continue
            # Koşulları kontrol et (örneğin: RSI < 30)
            operator, threshold = value[0], float(value[1:])
            actual_value = data.get(key)
            if operator == "<" and not (actual_value < threshold):
                return False
            elif operator == ">" and not (actual_value > threshold):
                return False
            # Diğer operatörler için ek kontroller ekleyebilirsiniz.
        return True

    def evaluate_logic(logic, conditions, data):
        if logic == "AND":
            return all(evaluate_condition(cond, data) for cond in conditions)
        elif logic == "OR":
            return any(evaluate_condition(cond, data) for cond in conditions)
        return False

    buy_conditions = parameters["buy"]
    return evaluate_logic(buy_conditions["logic"], buy_conditions["conditions"], data)
