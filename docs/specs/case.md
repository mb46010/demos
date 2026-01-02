We're building an AI assistant that helps managers write performance reviews. It takes bullet points as input and generates a draft review paragraph. Here's an example:"

# Input
Employee: Software Engineer, 2 years tenure
Rating: Exceeds expectations

Manager's bullets:
- Led migration of payment service to Kubernetes
- Reduced deployment time from 2 hours to 15 minutes
- Mentored two junior engineers
- Sometimes misses deadlines when overloaded

# Output
"Sarah has demonstrated exceptional performance this review period. She 
successfully led the critical migration of our payment service to Kubernetes, 
showcasing strong technical leadership. This initiative reduced deployment 
time by 87%, from 2 hours to just 15 minutes, significantly improving team 
velocity. Sarah has also invested in team growth by mentoring two junior 
engineers. While she occasionally faces challenges with deadline management 
during high-workload periods, her overall contributions have been outstanding."

The problem:

"HR and Legal are concerned about deploying this. They've raised these issues:

- Bias amplification — Could the model systematically write stronger reviews for certain groups?
- Fabrication — The model might add details not in the input (the '87%' wasn't in the bullets)
- Tone inconsistency — Different managers get different quality outputs
- Audit trail — If an employee disputes their review, can we show what the AI did vs. the manager?

How would you address these concerns? Pick two and go deep."

What they're evaluating:

- Can you think about AI risks concretely, not just abstractly?
- Do you propose practical mitigations or just identify problems?
- Understanding of fairness/bias in HR context
- System design for accountability

Follow-up questions:

"How would you detect if the model is biased against certain employee groups?"
"Should managers be required to edit the AI output, or can they submit as-is?"
"How do you handle the model writing something factually wrong about an employee?"