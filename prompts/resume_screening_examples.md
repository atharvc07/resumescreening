# Few-Shot Examples for Resume Screening

## Example 1: Strong Match

**Job Description:**
"Senior Python Developer with 5+ years experience in Django, PostgreSQL, and AWS deployment."

**Resume:**
"7 years Python development. Led Django projects at scale. Expert in PostgreSQL optimization. AWS certified."

**Expected Output:**
{
  "score": 92,
  "verdict": "STRONG_MATCH",
  "missing_requirements": [],
  "justification": "Candidate exceeds experience requirement (7 years vs 5 required) and demonstrates all key technical skills including Django, PostgreSQL, and AWS. The AWS certification adds additional credibility."
}

## Example 2: Partial Match

**Job Description:**
"Full-stack developer: React, Node.js, MongoDB, 3+ years experience."

**Resume:**
"2 years experience with React and Vue.js. Familiar with Express.js and MySQL."

**Expected Output:**
{
  "score": 58,
  "verdict": "PARTIAL_MATCH",
  "missing_requirements": [
    "3+ years experience (has only 2 years)",
    "Node.js experience (only Express.js mentioned)",
    "MongoDB experience (has MySQL instead)"
  ],
  "justification": "Candidate has strong React skills but falls short on experience timeline. While Express.js knowledge is relevant, explicit Node.js experience is not demonstrated. Database experience is with MySQL rather than required MongoDB."
}

## Example 3: No Match

**Job Description:**
"DevOps Engineer: Kubernetes, Terraform, CI/CD pipelines, 4+ years experience."

**Resume:**
"Junior Frontend Developer. 1 year experience with HTML, CSS, JavaScript. Intern projects with React."

**Expected Output:**
{
  "score": 15,
  "verdict": "NO_MATCH",
  "missing_requirements": [
    "Kubernetes experience",
    "Terraform experience",
    "CI/CD pipeline experience",
    "4+ years DevOps experience (candidate has 1 year in different field)"
  ],
  "justification": "Candidate's experience is entirely in frontend development with no demonstrated DevOps skills. The role requires infrastructure and automation expertise that is not present in the resume."
}
