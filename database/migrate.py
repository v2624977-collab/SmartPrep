import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pymysql
from werkzeug.security import generate_password_hash
from config import Config
from database.questions.gate_questions import gate_questions
from database.questions.tnpsc_questions import tnpsc_questions
from database.questions.ssc_questions import ssc_questions
from database.questions.cat_questions import cat_questions

# Baseline questions for exams 1 to 5 and TANCET Practice Quizzes 1 to 5 (IDs 1 to 125)
baseline_and_tancet_questions = [
    (1, 1, 'What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'Sequential Query Logic', 'System Query Language', 'A'),
    (2, 1, 'Which of the following is a non-linear data structure?', 'Array', 'Linked List', 'Tree', 'Stack', 'C'),
    (3, 1, 'Which scheduling algorithm is non-preemptive?', 'Round Robin', 'Shortest Job First (SJF)', 'Shortest Remaining Time First', 'Priority (Preemptive)', 'B'),
    (4, 1, 'What is the time complexity of binary search on a sorted array of size n?', 'O(n)', 'O(log n)', 'O(n log n)', 'O(1)', 'B'),
    (5, 1, 'In relational algebra, which operator is used for selection?', 'Sigma (σ)', 'Pi (π)', 'Rho (ρ)', 'Cartesian product (×)', 'A'),
    (6, 2, 'Which of the following problems is undecidable?', 'Halting problem of Turing machines', 'Membership in regular languages', 'Emptiness problem for finite automata', 'Context-free language equivalence with regular language', 'A'),
    (7, 2, 'In TCP/IP, which protocol operates at the Transport Layer?', 'IP', 'HTTP', 'TCP', 'ARP', 'C'),
    (8, 2, 'What is the maximum number of nodes in a binary tree of height h (root at height 0)?', '2^h', '2^(h+1) - 1', '2^(h-1)', '2^h - 1', 'B'),
    (9, 2, 'Which normal form eliminates partial functional dependencies?', '1NF', '2NF', '3NF', 'BCNF', 'B'),
    (10, 2, 'A pipeline with 5 stages has clock cycle of 10ns. What is the execution time for 100 instructions?', '1040 ns', '1000 ns', '500 ns', '5400 ns', 'A'),
    (11, 3, 'Who is known as the Father of the Indian Constitution?', 'Mahatma Gandhi', 'Dr. B. R. Ambedkar', 'Jawaharlal Nehru', 'Sardar Vallabhbhai Patel', 'B'),
    (12, 3, 'Which is the longest river in Peninsular India?', 'Godavari', 'Krishna', 'Cauvery', 'Mahanadi', 'A'),
    (13, 3, 'Under which Article of the Indian Constitution is the President Rule imposed in a State?', 'Article 352', 'Article 356', 'Article 360', 'Article 370', 'B'),
    (14, 3, 'The Sangam literature was composed in which language?', 'Tamil', 'Sanskrit', 'Pali', 'Prakrit', 'A'),
    (15, 3, 'Which Indian state has the highest literacy rate according to 2011 Census?', 'Kerala', 'Tamil Nadu', 'Goa', 'Maharashtra', 'A'),
    (16, 4, 'If A : B = 2 : 3 and B : C = 4 : 5, then what is A : B : C?', '8 : 12 : 15', '2 : 4 : 5', '6 : 8 : 10', '8 : 10 : 15', 'A'),
    (17, 4, 'Select the synonym of the word CANDID:', 'Secretive', 'Frank', 'Deceitful', 'Cruel', 'B'),
    (18, 4, 'A train running at 72 km/h crosses a 200m long platform in 20 seconds. What is the length of the train?', '200 m', '250 m', '150 m', '300 m', 'A'),
    (19, 4, 'Who was the first Governor-General of independent India?', 'Lord Mountbatten', 'C. Rajagopalachari', 'Lord Canning', 'Lord Dalhousie', 'A'),
    (20, 4, 'Which gas is known as Laughing Gas?', 'Nitric oxide', 'Nitrous oxide', 'Nitrogen dioxide', 'Nitrogen pentoxide', 'B'),
    (21, 5, 'If log_2 (x - 1) = 3, what is the value of x?', '7', '8', '9', '10', 'C'),
    (22, 5, 'In how many different ways can the letters of the word SMART be arranged?', '60', '120', '24', '720', 'B'),
    (23, 5, 'A shopkeeper marks an item 20% above cost and allows 10% discount. What is his profit percentage?', '8%', '10%', '12%', '15%', 'A'),
    (24, 5, 'Find the remainder when 2^50 is divided by 7.', '1', '2', '4', '6', 'C'),
    (25, 5, 'Two pipes A and B can fill a tank in 12 hours and 18 hours respectively. How long will they take together?', '7.2 hours', '6 hours', '8.5 hours', '10 hours', 'A'),
    (26, 6, 'What is 25% of 360?', '90', '80', '100', '75', 'A'),
    (27, 6, 'Identify the next number in the arithmetic sequence: 7, 12, 17, 22, ___.', '25', '27', '29', '31', 'B'),
    (28, 6, "Choose the word that is most nearly the SYNONYM of 'Abundant':", 'Scarce', 'Meager', 'Plentiful', 'Deficient', 'C'),
    (29, 6, 'In a certain code, if CAT is written as 3120 using alphabet positions (C=3, A=1, T=20), how will DOG be written?', '4147', '4158', '3157', '4157', 'D'),
    (30, 6, 'What is the full form of the computing term RAM?', 'Random Access Memory', 'Read Access Memory', 'Rapid Application Module', 'Remote Access Mode', 'A'),
    (31, 6, 'Calculate the Simple Interest on a principal of Rs. 2,000 at 5% per annum for 3 years.', 'Rs. 250', 'Rs. 300', 'Rs. 350', 'Rs. 400', 'B'),
    (32, 6, 'Find the odd one out among the following geometric shapes:', 'Square', 'Rectangle', 'Cube', 'Parallelogram', 'C'),
    (33, 6, "Select the word that is opposite in meaning (ANTONYM) to 'Diligent':", 'Industrious', 'Persistent', 'Attentive', 'Indolent', 'D'),
    (34, 6, 'A person walks 10 meters North, turns right and walks 10 meters. Which cardinal direction is he facing now?', 'East', 'West', 'North', 'South', 'A'),
    (35, 6, 'Find the arithmetic mean (average) of the numbers: 10, 20, 30, 40, and 50.', '25', '30', '35', '40', 'B'),
    (36, 6, 'Which of the following computer hardware components is an input device?', 'Laser Printer', 'LED Monitor', 'Optical Scanner', 'Audio Speaker', 'C'),
    (37, 6, "Pointing to a photograph of a boy, Suresh said, 'He is the son of my father\\'s only son.' Who is the boy to Suresh?", 'Brother', 'Nephew', 'Uncle', 'Son', 'D'),
    (38, 6, 'A retailer purchases an item for Rs. 400 and sells it for Rs. 480. What is the profit percentage?', '20%', '25%', '15%', '18%', 'A'),
    (39, 6, "Fill in the blank with the grammatically correct option: 'The earth ______ around the sun.'", 'is revolving', 'revolves', 'revolved', 'has revolved', 'B'),
    (40, 6, 'Complete the letter series: B, D, F, H, ___.', 'I', 'K', 'J', 'L', 'C'),
    (41, 6, 'If a bus travels a total distance of 180 km in 3 hours at uniform speed, what is its average speed?', '50 km/h', '55 km/h', '65 km/h', '60 km/h', 'D'),
    (42, 6, 'Which of the following is considered an operating system software?', 'Linux', 'Microsoft Word', 'Google Chrome', 'Adobe Acrobat', 'A'),
    (43, 6, 'In a certain code language, if BOOK is written as C P P L, then how will READ be written?', 'S G C F', 'S F B E', 'S E B C', 'T F B E', 'B'),
    (44, 6, 'Choose the correctly spelt word from the options below:', 'Acomodate', 'Acommodate', 'Accommodate', 'Accomadate', 'C'),
    (45, 6, 'In a class of 50 students, the ratio of boys to girls is 3 : 2. How many boys are there in the class?', '20', '25', '35', '30', 'D'),
    (46, 7, 'If the price of sugar increases by 25%, by what percentage must a family reduce its consumption to keep expenditure unchanged?', '20%', '25%', '15%', '16.66%', 'A'),
    (47, 7, 'Find the missing number in the geometric series: 3, 9, 27, 81, ___.', '162', '243', '324', '729', 'B'),
    (48, 7, "Select the appropriate preposition: 'She has been studying in this institute ______ 2022.'", 'for', 'from', 'since', 'by', 'C'),
    (49, 7, "If 'TABLE' is coded as 'GZYOV', how will 'CHAIR' be coded using the reverse alphabet cipher (A<->Z, B<->Y)?", 'XSRZI', 'XSZRK', 'XTRZI', 'XSZRI', 'D'),
    (50, 7, 'Two numbers are in the ratio 4 : 5 and their Least Common Multiple (LCM) is 180. What is the smaller number?', '36', '45', '30', '40', 'A'),
    (51, 7, 'A train 150 meters long crosses a stationary telegraph pole in 10 seconds. Find the speed of the train in km/h.', '48 km/h', '54 km/h', '60 km/h', '72 km/h', 'B'),
    (52, 7, "Choose the antonym of the word 'CANDID':", 'Sincere', 'Outspoken', 'Deceptive', 'Frank', 'C'),
    (53, 7, 'If A is the sister of B, B is the daughter of C, and D is the husband of C, how is D related to A?', 'Brother', 'Uncle', 'Grandfather', 'Father', 'D'),
    (54, 7, 'A trader offers two successive discounts of 10% and 20% on an article marked at Rs. 1,000. What is the final selling price?', 'Rs. 720', 'Rs. 700', 'Rs. 750', 'Rs. 680', 'A'),
    (55, 7, 'Which protocol is universally used to securely transfer hypertext documents over the World Wide Web?', 'FTP', 'HTTPS', 'SMTP', 'TELNET', 'B'),
    (56, 7, 'Find the next term in the alphanumeric series: A1, C3, E5, G7, ___.', 'H8', 'I10', 'I9', 'J9', 'C'),
    (57, 7, 'The average age of 4 members in a family is 25 years. If a child aged 5 years is added, what becomes the new average age?', '20 years', '22 years', '23 years', '21 years', 'D'),
    (58, 7, "Identify the segment with a grammatical error: 'Neither the manager (A) / nor his assistants (B) / was present at the meeting (C) / No error (D)'", 'was present at the meeting', 'Neither the manager', 'nor his assistants', 'No error', 'A'),
    (59, 7, 'A clock shows exactly 3:00. What is the angle between the hour hand and the minute hand?', '60 degrees', '90 degrees', '75 degrees', '105 degrees', 'B'),
    (60, 7, 'Pipe A can fill a water tank in 6 hours, while Pipe B can fill the same tank in 12 hours. How long will they take working together?', '3 hours', '5 hours', '4 hours', '8 hours', 'C'),
    (61, 7, 'In a row of 30 students, Priya is 12th from the left end. What is her rank from the right end?', '18th', '20th', '21st', '19th', 'D'),
    (62, 7, "Select the synonym for the word 'METICULOUS':", 'Punctilious', 'Careless', 'Hasty', 'Vague', 'A'),
    (63, 7, 'The perimeter of a rectangular field is 120 meters and its length is 40 meters. Find its area.', '600 sq m', '800 sq m', '1000 sq m', '1200 sq m', 'B'),
    (64, 7, 'Which computer data structure operates strictly on the Last-In-First-Out (LIFO) access principle?', 'Queue', 'Linked List', 'Stack', 'Binary Tree', 'C'),
    (65, 7, "If '+' denotes multiplication, '-' denotes addition, and '*' denotes division, what is the value of: 12 + 3 - 6 * 2?", '36', '38', '42', '39', 'D'),
    (66, 8, 'A can complete a piece of work in 10 days and B can do it in 15 days. If they work together for 4 days, what fraction of the work remains unfinished?', '1/3', '1/4', '5/12', '7/18', 'A'),
    (67, 8, 'A motorboat travels 24 km downstream in 2 hours and 16 km upstream in 4 hours. What is the speed of the water current?', '1 km/h', '4 km/h', '2 km/h', '3 km/h', 'B'),
    (68, 8, 'Statements: Some pens are pencils. All pencils are erasers. Conclusions: I. Some erasers are pens. II. Some pens are not erasers. Which conclusion logically follows?', 'Only II follows', 'Neither I nor II follows', 'Only I follows', 'Both I and II follow', 'C'),
    (69, 8, 'What principal sum lent at Compound Interest will amount to Rs. 2,420 in 2 years at an interest rate of 10% per annum compounded annually?', 'Rs. 1,800', 'Rs. 1,950', 'Rs. 2,100', 'Rs. 2,000', 'D'),
    (70, 8, "Choose the correct one-word substitute: 'A person who remains indifferent to both pleasure and pain.'", 'Stoic', 'Ascetic', 'Epicurean', 'Hedonist', 'A'),
    (71, 8, 'A train running at 72 km/h crosses a platform 250 meters long in 20 seconds. What is the length of the train?', '120 meters', '150 meters', '180 meters', '200 meters', 'B'),
    (72, 8, 'In a survey of 100 students, 60 like tea, 50 like coffee, and 20 like both beverages. How many students like neither tea nor coffee?', '15', '20', '10', '25', 'C'),
    (73, 8, 'If log_10 (2) = 0.3010, what is the numerical value of log_10 (5)?', '0.4771', '0.6020', '0.7781', '0.6990', 'D'),
    (74, 8, 'Select the sentence with correct subject-verb agreement:', 'The committee has submitted its annual audit report.', 'The committee have submitted its annual audit report.', 'The committee has submit their annual audit report.', 'The committee are submitting its annual audit report.', 'A'),
    (75, 8, 'Six people P, Q, R, S, T, and U sit in a circle facing the center. P is directly opposite to S. Q is to the immediate right of P. If positions are 1 to 6 clockwise with P at 1, Q at 2, S at 4, who sits directly opposite to Q?', 'R', 'T', 'U', 'P', 'B'),
    (76, 8, "The ratio of present ages of Arun and Varun is 4 : 5. Six years hence, the ratio of their ages will become 5 : 6. What is Arun's current age?", '18 years', '20 years', '24 years', '28 years', 'C'),
    (77, 8, 'A shopkeeper marks goods 40% above the cost price and allows a discount of 15% on cash payment. What is his net gain percentage?', '22%', '20%', '21%', '19%', 'D'),
    (78, 8, 'Which sorting algorithm has a guaranteed worst-case time complexity of O(n log n)?', 'Merge Sort', 'Quick Sort', 'Bubble Sort', 'Insertion Sort', 'A'),
    (79, 8, 'Find the missing number in the sequence: 4, 18, 48, 100, 180, ___.', '252', '294', '312', '276', 'B'),
    (80, 8, "Identify the meaning of the idiom: 'To throw in the towel'", 'To accept a new challenge', 'To postpone a decision', 'To surrender or admit defeat', 'To clean up a mistake', 'C'),
    (81, 8, 'Two unbiased dice are thrown simultaneously. What is the mathematical probability of obtaining a total score of 7?', '1/12', '1/9', '5/36', '1/6', 'D'),
    (82, 8, 'In an office, 40% of employees are male and 60% are female. If 70% of males and 80% of females are graduates, what percentage of all employees are graduates?', '76%', '74%', '72%', '78%', 'A'),
    (83, 8, "In a code language, 134 means 'good and tasty', 478 means 'see good pictures', and 729 means 'pictures are faint'. Which digit stands for 'see'?", '4', '8', '7', '9', 'B'),
    (84, 8, 'A cylinder has radius 7 cm and height 10 cm. Find its total surface area. (Take pi = 22/7)', '660 sq cm', '724 sq cm', '748 sq cm', '792 sq cm', 'C'),
    (85, 8, 'Complete the analogy: Ephemeral : Permanent :: Obscure : ___', 'Hidden', 'Ambiguous', 'Doubtful', 'Lucid', 'D'),
    (86, 9, "In how many distinct permutations can the letters of the word 'MANAGEMENT' be arranged?", '226,800', '453,600', '567,000', '1,134,000', 'A'),
    (87, 9, 'A bag contains 5 red, 4 green, and 3 blue marbles. If 3 marbles are drawn at random without replacement, what is the probability that all 3 are red?', '1/11', '1/22', '5/44', '3/22', 'B'),
    (88, 9, 'If x + 1/x = 4, find the numerical value of x^3 + 1/x^3.', '48', '64', '52', '56', 'C'),
    (89, 9, 'A can do a piece of work in 20 days and B in 30 days. They work together for 5 days, and then A leaves. In how many more days will B finish the remaining work alone?', '14 days', '15 days', '16 days', '17.5 days', 'D'),
    (90, 9, 'Select the word that represents the best analogy: Catalyst : Reaction :: Incentive : ___', 'Production', 'Reluctance', 'Stagnation', 'Penalty', 'A'),
    (91, 9, 'Six delegates A, B, C, D, E, F sit in a row facing North. B is between D and F. E is between A and C. A does not sit next to D or F. C does not sit next to D. F is to the immediate right of C. Who sits second from the right end?', 'F', 'B', 'D', 'E', 'B'),
    (92, 9, 'The compound interest on a certain sum for 2 years at 12% per annum is Rs. 1,590. What is the simple interest on the same principal for the same period and rate?', 'Rs. 1,450', 'Rs. 1,480', 'Rs. 1,500', 'Rs. 1,520', 'C'),
    (93, 9, 'Find the remainder when 3^65 is divided by 8.', '1', '7', '5', '3', 'D'),
    (94, 9, "Identify the grammatically correct passive voice conversion: 'The authorities are constructing a new expressway across the valley.'", 'A new expressway is being constructed across the valley by the authorities.', 'A new expressway was constructed across the valley by the authorities.', 'A new expressway has been constructed across the valley by the authorities.', 'A new expressway is constructed across the valley by the authorities.', 'A'),
    (95, 9, 'A motorboat whose speed in still water is 15 km/h travels 30 km downstream and returns in a total time of 4 hours 30 minutes. What is the speed of the river stream?', '4 km/h', '5 km/h', '6 km/h', '3 km/h', 'B'),
    (96, 9, 'How many integers strictly between 100 and 600 are divisible by both 4 and 6?', '39', '40', '41', '42', 'C'),
    (97, 9, 'Statements: No country is an island. All islands are secluded. Some secluded places are quiet. Which conclusion necessarily follows?', 'All quiet places are islands', 'No country is secluded', 'Some islands are quiet', 'Some secluded places are not countries', 'D'),
    (98, 9, 'If alpha and beta are roots of the quadratic equation 2x^2 - 7x + 3 = 0, find the value of (alpha^2 + beta^2).', '37/4', '41/4', '31/4', '25/4', 'A'),
    (99, 9, 'A vendor mixes two varieties of rice costing Rs. 38/kg and Rs. 48/kg and sells the mixture at Rs. 46.20/kg, making a 10% profit. What is the mixing ratio?', '2 : 3', '3 : 2', '4 : 3', '5 : 4', 'B'),
    (100, 9, "Read the statement: 'Despite heavy economic sanctions, the country achieved 4% GDP expansion.' What is the underlying assumption?", 'Sanctions always increase industrial growth.', 'The country relies entirely on external financial support.', 'Economic sanctions typically suppress or hinder GDP growth.', 'GDP expansion has no relationship with global trade.', 'C'),
    (101, 9, 'Find the sum of all integers from 1 to 100 that are NOT divisible by 3.', '3280', '3420', '3315', '3367', 'D'),
    (102, 9, 'What is the shortest distance between the origin (0,0) and the point of intersection of the lines 3x + 4y = 25 and 4x - 3y = 0?', '5 units', '6 units', '4 units', '7 units', 'A'),
    (103, 9, "Choose the antonym of the word 'EQUIVOCAL':", 'Vague', 'Unambiguous', 'Deceptive', 'Obscure', 'B'),
    (104, 9, 'In a college election between two candidates, the winner obtained 58% of the votes and won by a majority of 480 votes. Assuming no invalid votes, what was the total number of votes cast?', '2,800', '3,200', '3,000', '3,600', 'C'),
    (105, 9, 'A solid metallic sphere of radius 6 cm is melted and recast into small cones of radius 2 cm and height 3 cm each. How many such cones can be formed?', '64', '80', '84', '72', 'D'),
    (106, 10, 'If log_2 (x) + log_4 (x) + log_16 (x) = 21/4, find the positive value of x.', '8', '16', '4', '32', 'A'),
    (107, 10, 'Three taps A, B, and C can fill an empty reservoir in 10, 20, and 30 hours respectively. Tap A is opened all the time, while B and C are opened alternately for 1 hour each, beginning with B. In how many hours will the reservoir be filled completely?', '6.5 hours', '7 hours', '8 hours', '7.5 hours', 'B'),
    (108, 10, 'A committee of 5 members is to be formed from 6 men and 4 women. In how many ways can this be done if the committee must contain at least 3 women?', '62', '76', '66', '72', 'C'),
    (109, 10, 'Two trains of lengths 140 m and 160 m run on parallel tracks in opposite directions at 60 km/h and 48 km/h respectively. In how many seconds will they pass each other completely from the moment they meet?', '12 seconds', '15 seconds', '8 seconds', '10 seconds', 'D'),
    (110, 10, 'Evaluate the numerical expression: (2.39^2 - 1.61^2) / (2.39 - 1.61).', '4.00', '0.78', '3.78', '4.20', 'A'),
    (111, 10, 'A container has 80 liters of pure milk. From this, 8 liters are drawn out and replaced with water. This replacement procedure is repeated two more times. How many liters of pure milk remain in the container?', '52.48 liters', '58.32 liters', '56.12 liters', '60.48 liters', 'B'),
    (112, 10, 'Five corporate executives A, B, C, D, and E hold ranks CEO, CFO, COO, CMO, and CTO (highest to lowest). CEO is not A or E. B is ranked immediately higher than D. The CFO is ranked immediately higher than C. E is ranked lower than COO but is not CTO. Who holds the rank of COO?', 'B', 'D', 'C', 'A', 'C'),
    (113, 10, 'Find the units digit of the huge mathematical expression: (7^95 - 3^58).', '2', '6', '0', '4', 'D'),
    (114, 10, "Select the word that best completes the sentence with appropriate connotation: 'The CEO delivered a ______ critique that dissects every flawed assumption in the proposal with clinical precision.'", 'trenchant', 'superficial', 'equivocal', 'convoluted', 'A'),
    (115, 10, 'A watch gains 5 seconds in 3 minutes and was set right at 8:00 AM. What time will it show in the afternoon of the same day when the true time is 2:00 PM?', '2:05 PM', '2:10 PM', '2:15 PM', '2:08 PM', 'B'),
    (116, 10, 'In an acute-angled triangle ABC, altitude AD = 12 cm, side AB = 13 cm, and side AC = 15 cm. Find the length of base BC.', '12 cm', '13 cm', '14 cm', '16 cm', 'C'),
    (117, 10, 'A box holds 4 black balls, 3 white balls, and 5 red balls. If 2 balls are chosen at random, what is the probability that neither ball is white?', '5/11', '7/22', '8/11', '6/11', 'D'),
    (118, 10, "Consider the logical implication: 'If market volatility exceeds 18%, automated risk stops trigger liquidation.' Which statement is the Contrapositive?", 'If automated risk stops do not trigger liquidation, then market volatility does not exceed 18%.', 'If automated risk stops trigger liquidation, then market volatility exceeds 18%.', 'If market volatility does not exceed 18%, then automated risk stops do not trigger liquidation.', 'Market volatility exceeds 18% only when risk stops trigger liquidation.', 'A'),
    (119, 10, 'The difference between compound interest (compounded annually) and simple interest on a sum at 15% per annum for 3 years is Rs. 1,134. Find the principal sum.', 'Rs. 15,000', 'Rs. 16,000', 'Rs. 18,000', 'Rs. 20,000', 'B'),
    (120, 10, "Identify the fallacy in the reasoning: 'Every player on this football team is a world-class superstar, therefore this team will be the greatest team ever assembled.'", 'Ad Hominem', 'Post Hoc Ergo Propter Hoc', 'Fallacy of Composition', 'False Dichotomy', 'C'),
    (121, 10, 'How many pairs of positive integers (x, y) satisfy the linear Diophantine equation 7x + 12y = 220?', '1 pair', '2 pairs', '4 pairs', '3 pairs', 'D'),
    (122, 10, 'A trader blends two grades of tea costing Rs. 180/kg and Rs. 260/kg in the ratio 5 : 3. If he sells the combined blend at Rs. 240/kg, what is his exact profit percentage?', '14.28%', '16.66%', '12.50%', '15.00%', 'A'),
    (123, 10, 'Which of the following sentences exhibits correct use of the subjunctive mood in English grammar?', 'The committee insists that the chairman resigns immediately.', 'The committee insists that the chairman resign immediately.', 'The committee insists that the chairman is resigning immediately.', 'The committee insists that the chairman has resigned immediately.', 'B'),
    (124, 10, 'A and B start a partnership with initial capitals in ratio 3 : 5. After 4 months, A invests 50% more capital while B withdraws 20% of his capital. What is the ratio of their profits after 1 year?', '11 : 13', '10 : 13', '12 : 13', '13 : 14', 'C'),
    (125, 10, 'An urn contains 4 white, 5 red, and 6 green chips. Three chips are drawn at random without replacement. Find the probability that at least one of the drawn chips is red.', '24/91', '55/91', '37/91', '67/91', 'D')
]

all_practice_questions = baseline_and_tancet_questions + gate_questions + tnpsc_questions + ssc_questions + cat_questions

all_exams = [
    # 5 Primary Competitive Exams
    (1, 'TANCET', 'Tamil Nadu Common Entrance Test - Postgraduate entrance exam for MBA and MCA programs across Tamil Nadu institutions.', 30),
    (2, 'GATE', 'Graduate Aptitude Test in Engineering - National examination testing comprehensive understanding in Computer Science & Information Technology.', 30),
    (3, 'TNPSC Group 4', 'Tamil Nadu Public Service Commission Group 4 Examination - Comprehensive recruitment exam covering General Studies, Aptitude, and Language.', 30),
    (4, 'SSC CGL', 'Staff Selection Commission Combined Graduate Level - Premier national recruitment examination for Group B and Group C government positions.', 30),
    (5, 'CAT', 'Common Admission Test - Premier national computer-based management aptitude test for admissions into IIMs and top management institutes.', 30),

    # TANCET Practice Series (6 to 10)
    (6, 'TANCET Practice Quiz 1', 'TANCET Practice Quiz 1 - 20 Questions - Easy. Foundational quantitative aptitude, vocabulary, and basic logical reasoning.', 25),
    (7, 'TANCET Practice Quiz 2', 'TANCET Practice Quiz 2 - 20 Questions - Easy to Moderate. Percentages, coding-decoding, sentence correction, and data relations.', 25),
    (8, 'TANCET Practice Quiz 3', 'TANCET Practice Quiz 3 - 20 Questions - Moderate. Time and work, speed-distance, syllogisms, reading comprehension, and business data analysis.', 30),
    (9, 'TANCET Practice Quiz 4', 'TANCET Practice Quiz 4 - 20 Questions - Moderate to Difficult. Permutations, probability, seating arrangements, critical reasoning, and algebra.', 30),
    (10, 'TANCET Practice Quiz 5', 'TANCET Practice Quiz 5 - 20 Questions - Difficult. Multi-step data interpretation, complex analytical puzzles, logarithmic equations, and verbal analogies.', 35),

    # GATE Practice Series (11 to 15)
    (11, 'GATE Practice Quiz 1', 'GATE Practice Quiz 1 - 20 Questions - Easy. Foundational concepts in discrete math, digital logic, data structures, and computer organization.', 25),
    (12, 'GATE Practice Quiz 2', 'GATE Practice Quiz 2 - 20 Questions - Easy to Moderate. Linear algebra, operating systems, DBMS normalization, regular languages, and networks.', 25),
    (13, 'GATE Practice Quiz 3', 'GATE Practice Quiz 3 - 20 Questions - Moderate. Pipelining, graph algorithms, compiler parsing, subnetting, and process synchronization.', 30),
    (14, 'GATE Practice Quiz 4', 'GATE Practice Quiz 4 - 20 Questions - Moderate to Difficult. Memory hierarchy, B+ trees, dynamic programming, context-free languages, and TCP congestion.', 30),
    (15, 'GATE Practice Quiz 5', 'GATE Practice Quiz 5 - 20 Questions - Difficult. Decidability, advanced cache analysis, complex recursive complexities, and database serializability.', 35),

    # TNPSC Group 4 Practice Series (16 to 20)
    (16, 'TNPSC Group 4 Practice Quiz 1', 'TNPSC Group 4 Practice Quiz 1 - 20 Questions - Easy. General Science basics, Indian Polity preamble, simple LCM/HCF aptitude, and Tamil Nadu heritage.', 25),
    (17, 'TNPSC Group 4 Practice Quiz 2', 'TNPSC Group 4 Practice Quiz 2 - 20 Questions - Easy to Moderate. Fundamental rights, Sangam era, percentages, geography of Tamil Nadu, and basic physics.', 25),
    (18, 'TNPSC Group 4 Practice Quiz 3', 'TNPSC Group 4 Practice Quiz 3 - 20 Questions - Moderate. Compound interest, time and work, Directive Principles, rivers of India, and Tirukkural concepts.', 30),
    (19, 'TNPSC Group 4 Practice Quiz 4', 'TNPSC Group 4 Practice Quiz 4 - 20 Questions - Moderate to Difficult. Panchayati Raj amendments, freedom movements in Tamil Nadu, ratio-proportion, and Indian economy.', 30),
    (20, 'TNPSC Group 4 Practice Quiz 5', 'TNPSC Group 4 Practice Quiz 5 - 20 Questions - Difficult. Multi-statement constitutional provisions, advanced mensuration, economic planning, and Tamil literary history.', 35),

    # SSC CGL Practice Series (21 to 25)
    (21, 'SSC CGL Practice Quiz 1', 'SSC CGL Practice Quiz 1 - 20 Questions - Easy. Foundational arithmetic, vocabulary synonyms/antonyms, alphabet series, and basic general awareness.', 25),
    (22, 'SSC CGL Practice Quiz 2', 'SSC CGL Practice Quiz 2 - 20 Questions - Easy to Moderate. Ratios, profit and loss, blood relations, error detection, and medieval Indian history.', 25),
    (23, 'SSC CGL Practice Quiz 3', 'SSC CGL Practice Quiz 3 - 20 Questions - Moderate. Trigonometry, circle geometry, syllogisms, active/passive voice, and Indian economic terms.', 30),
    (24, 'SSC CGL Practice Quiz 4', 'SSC CGL Practice Quiz 4 - 20 Questions - Moderate to Difficult. Algebraic identities, 3D mensuration, direct/indirect narration, seating arrangements, and constitutional articles.', 30),
    (25, 'SSC CGL Practice Quiz 5', 'SSC CGL Practice Quiz 5 - 20 Questions - Difficult. Advanced geometry tangents, complex arithmetic progressions, critical reasoning, and high-level vocabulary idioms.', 35),

    # CAT Practice Series (26 to 30)
    (26, 'CAT Practice Quiz 1', 'CAT Practice Quiz 1 - 20 Questions - Easy. Averages, percentages, linear arrangements, para-jumbles, and basic quantitative arithmetic.', 25),
    (27, 'CAT Practice Quiz 2', 'CAT Practice Quiz 2 - 20 Questions - Easy to Moderate. Time-speed-distance, quadratic equations, Venn diagram logic, sentence completion, and critical reasoning.', 25),
    (28, 'CAT Practice Quiz 3', 'CAT Practice Quiz 3 - 20 Questions - Moderate. Logarithms, permutations and combinations, tabular data interpretation, and passage inference.', 30),
    (29, 'CAT Practice Quiz 4', 'CAT Practice Quiz 4 - 20 Questions - Moderate to Difficult. Number theory remainders, maxima-minima, multi-parameter grid puzzles, and para-summary.', 30),
    (30, 'CAT Practice Quiz 5', 'CAT Practice Quiz 5 - 20 Questions - Difficult. Advanced geometry & coordinate geometry, complex modular arithmetic, tournament brackets, and nuanced RC inference.', 35),
]

def run_migration():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    # 1. Add duration_minutes to exam if not exists
    cursor.execute("SHOW COLUMNS FROM exam LIKE 'duration_minutes'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE exam ADD COLUMN duration_minutes INT DEFAULT 30")
        print("Added duration_minutes to exam table.")

    # 2. Add total_questions and percentage to result if not exists
    cursor.execute("SHOW COLUMNS FROM result LIKE 'total_questions'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE result ADD COLUMN total_questions INT DEFAULT 0")
        print("Added total_questions to result table.")

    cursor.execute("SHOW COLUMNS FROM result LIKE 'percentage'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE result ADD COLUMN percentage FLOAT DEFAULT 0.0")
        print("Added percentage to result table.")

    # 3. Create password_reset_token table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_token (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            token_hash VARCHAR(255) NOT NULL,
            expires_at DATETIME NOT NULL,
            used TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
        );
    """)
    print("Ensured password_reset_token table exists.")

    # 4. Add default admin if admin table is empty
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        admin_pw = generate_password_hash("admin123")
        cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", ("admin", admin_pw))
        print("Seeded default admin (admin / admin123).")

    # 4. Seed all 30 exams
    for ex in all_exams:
        cursor.execute("""
            INSERT INTO exam (exam_id, exam_name, description, duration_minutes)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE exam_name=VALUES(exam_name), description=VALUES(description), duration_minutes=VALUES(duration_minutes)
        """, ex)
    print(f"Successfully seeded {len(all_exams)} exams and practice quizzes.")

    # 5. Seed all questions
    for q in all_practice_questions:
        cursor.execute("""
            INSERT INTO question (question_id, exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE exam_id=VALUES(exam_id), question_text=VALUES(question_text), option_a=VALUES(option_a), option_b=VALUES(option_b), option_c=VALUES(option_c), option_d=VALUES(option_d), correct_answer=VALUES(correct_answer)
        """, q)
    print(f"Successfully seeded {len(all_practice_questions)} questions across all exams.")

    # 6. Fix existing results total_questions and percentage
    cursor.execute("SELECT result_id, exam_id, score, total_questions FROM result")
    rows = cursor.fetchall()
    for r in rows:
        rid, eid, score, total_q = r
        if not total_q or total_q == 0:
            cursor.execute("SELECT count(*) FROM question WHERE exam_id=%s", (eid,))
            qcount = cursor.fetchone()[0] or 1
            pct = round((score / qcount) * 100, 2)
            cursor.execute("UPDATE result SET total_questions=%s, percentage=%s WHERE result_id=%s", (qcount, pct, rid))

    conn.commit()
    cursor.close()
    conn.close()
    print("Database migration and question seeding completed successfully!")

if __name__ == "__main__":
    run_migration()
