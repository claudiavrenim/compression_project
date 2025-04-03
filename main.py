import pandas as pd

#declaring functions for reading
def read_dataset(file_path):
    return pd.read_csv(file_path, sep='\t')

def read_rules(file_path):
    with open(file_path, 'r') as f:
        #create list without empty lines and blank spaces
        rules = [line.strip() for line in f if line.strip()]
    return rules

def compress_rules(rules):
    compressed_rules=[]
    #split the rules in lhs and rhs
    for rule in rules:
        lhs = rule.split(" => ")[0]
        rhs = rule.split(" => ")[1]
#check redundancy: check the condition of subset
        is_redundant = False
        for existing_rule in compressed_rules:
            existing_lhs = existing_rule.split(" => ")[0]
            if set(existing_lhs.split(" AND ")).issubset(set(lhs.split(" AND "))):
                is_redundant = True
                break
        if not is_redundant:
            compressed_rules.append(rule)
            
    compressed_rules = merge_rules(compressed_rules)        
    return compressed_rules    

def merge_rules(rules):
    # merge rules with similar conditions
    merged_rules = []
    # put together rules with same RHS
    for rule in rules:
        lhs = rule.split(" => ")[0]
        rhs = rule.split(" => ")[1]
        # Look for rules that can be merged
        merged = False
        for i, existing_rule in enumerate(merged_rules):
            existing_lhs = existing_rule.split(" => ")[0]
            # Compare LHS conditions
            if can_merge(lhs, existing_lhs):
                # merge rules
                new_lhs = merge_conditions(lhs, existing_lhs)
                merged_rules[i] = f"{new_lhs} => {rhs}"
                merged = True
                break
        # add the rule
        if not merged:
            merged_rules.append(rule)
    return merged_rules

def can_merge(lhs1, lhs2):
    #check if two LHS conditions can be merged 
    conditions1 = set(lhs1.split(" AND "))
    conditions2 = set(lhs2.split(" AND "))
    return len(conditions1.intersection(conditions2)) > 0

def merge_conditions(lhs1, lhs2):
    #merge LHS conditions
    conditions1 = set(lhs1.split(" AND "))
    conditions2 = set(lhs2.split(" AND "))
    # Find common conditions
    common_conditions = conditions1.intersection(conditions2) 
    # Find unique conditions for each rule
    unique_conditions1 = conditions1.difference(common_conditions)
    unique_conditions2 = conditions2.difference(common_conditions)
    # Combine conditions with OR
    combined_unique = " OR ".join(sorted(unique_conditions1.union(unique_conditions2)))
    # Return the new and combined rule
    if combined_unique:
        return " AND ".join(sorted(common_conditions)) + " AND (" + combined_unique + ")"
    else:
        return " AND ".join(sorted(common_conditions))    
    
def evaluate_rule_support(rule, dataset):
    #evaluate how many times a rule is satisfied in the dataset with return: number of rows in the dataset where the rule is true 
    lhs = rule.split(" => ")[0]  
    conditions = lhs.split(" AND ")  
    mask = pd.Series([True] * len(dataset))  
    for condition in conditions:
        if condition.startswith("NOT "):
            # Negation of a biomark
            biomarker = condition[4:]  # Remove "NOT "
            mask &= ~dataset[biomarker].astype(bool)  # Negation
        else:
            mask &= dataset[condition].astype(bool)
    # says how many rows satisfy the rule
    return mask.sum()

def calculate_rule_score(rule, dataset):
    #compute score of a rule combining support and specificity
    lhs = rule.split(" => ")[0]
    conditions = lhs.split(" AND ")
    support = evaluate_rule_support(rule, dataset)
    specificity_penalty = len(conditions)  
    score = support / (1 + specificity_penalty)  # Formula 
    return score

def rank_rules_by_usefulness(rules, dataset):
    #rank rules and return: list of (rule, score) ranked decreasingly 
    scored_rules = []
    for rule in rules:
        score = calculate_rule_score(rule, dataset)
        scored_rules.append((rule, score))
    # Rank rules by decreasing score
    scored_rules.sort(key=lambda x: x[1], reverse=True)
    return scored_rules

def save_compressed_rules(rules, score, output_file):
    with open(output_file, 'w') as f:
        for rule, score in zip(rules, score):
            f.write(f"Rule: {rule} | Score: {score:.2f}\n")

def main(dataset_file, rules_file, output_file):
    # Read the dataset
    dataset = read_dataset(dataset_file)
    print("Dataset columns:", dataset.columns.tolist())  # Print the dataset columns
    # Read the rules
    rules = read_rules(rules_file)
    print("Rules read:", rules)  # Print the rules read from the file
    # Calculate the scores of the rules
    scored_rules = rank_rules_by_usefulness(rules, dataset)
    print("Rule scores:", scored_rules)  # Print the rule scores
    # Filter significant rules
    threshold = 0.5
    rules = [rule for rule, score in scored_rules if score > threshold]
    scores = [score for rule, score in scored_rules]
    # Compress the rules
    compressed_rules = compress_rules(rules)
    print("Compressed rules:", compressed_rules)  # Print the compressed rules
    # Save the compressed rules with their scores
    save_compressed_rules(compressed_rules, scores, output_file)
    print(f"Compressed rules saved in {output_file}")

if __name__ == "__main__":
    dataset_file = "dataset.tsv"  # Your dataset file
    rules_file = "rules.txt"          # Your rules file
    output_file = "output_compressed_rules.txt"  # Output file
    main(dataset_file, rules_file, output_file) 

       