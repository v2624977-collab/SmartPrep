# GATE CSE Practice Questions (100 Questions)
# Exam IDs 11 to 15 (5 Quizzes x 20 Questions)

gate_questions = [
    # -------------------------------------------------------------
    # GATE PRACTICE QUIZ 1 (Exam ID: 11) - Easy (20 Questions)
    # Topics: Discrete Math, Digital Logic, DS, Basic OS, Networks, DBMS
    # -------------------------------------------------------------
    (
        126, 11,
        "Which of the following propositional logic expressions is a tautology?",
        "P v ~P", "P ^ ~P", "P -> ~P", "~P -> P",
        "A"
    ),
    (
        127, 11,
        "What is the minimum number of NAND gates required to implement a 2-input XOR gate?",
        "3", "4", "5", "6",
        "B"
    ),
    (
        128, 11,
        "In a complete binary tree with n leaf nodes, how many nodes have two children?",
        "n", "n + 1", "n - 1", "2n",
        "C"
    ),
    (
        129, 11,
        "What is the worst-case time complexity of inserting an element into a max-heap of n elements?",
        "O(n)", "O(n log n)", "O(1)", "O(log n)",
        "D"
    ),
    (
        130, 11,
        "Which CPU scheduling algorithm is guaranteed to minimize average waiting time for a given set of processes?",
        "Shortest Job First (SJF)", "First-Come, First-Served (FCFS)", "Round Robin (RR)", "Priority Scheduling",
        "A"
    ),
    (
        131, 11,
        "In relational databases, which of the following is an ACID property that ensures either all operations of a transaction take effect or none do?",
        "Isolation", "Atomicity", "Consistency", "Durability",
        "B"
    ),
    (
        132, 11,
        "What is the maximum data rate of a noiseless channel with bandwidth 4 kHz and 4-level signaling according to the Nyquist formula?",
        "8 kbps", "12 kbps", "16 kbps", "32 kbps",
        "C"
    ),
    (
        133, 11,
        "Which phase of a compiler generates syntax trees from a stream of tokens?",
        "Lexical Analysis", "Semantic Analysis", "Intermediate Code Generation", "Syntax Analysis",
        "D"
    ),
    (
        134, 11,
        "A graph with V vertices and E edges is represented using an adjacency matrix. What is the space complexity?",
        "O(V^2)", "O(V + E)", "O(E^2)", "O(V * E)",
        "A"
    ),
    (
        135, 11,
        "If a language L is accepted by a Finite Automaton, then L is guaranteed to be:",
        "Context-Free", "Regular", "Context-Sensitive", "Recursive",
        "B"
    ),
    (
        136, 11,
        "How many select lines are required for a 32-to-1 Multiplexer?",
        "4", "6", "5", "8",
        "C"
    ),
    (
        137, 11,
        "Which of the following IP address classes reserves the leading bits '110'?",
        "Class A", "Class B", "Class D", "Class C",
        "D"
    ),
    (
        138, 11,
        "In a demand-paging operating system, page table lookups are accelerated by using a specialized hardware buffer known as:",
        "Translation Lookaside Buffer (TLB)", "Memory Management Unit (MMU)", "Page Frame Table", "Direct Memory Access (DMA)",
        "A"
    ),
    (
        139, 11,
        "What is the sum of the degrees of all vertices in any undirected graph with E edges?",
        "E", "2E", "E / 2", "E^2",
        "B"
    ),
    (
        140, 11,
        "Which of the following database anomalies is eliminated when a relation is normalized to Second Normal Form (2NF)?",
        "Transitive Dependency", "Lossless Join Anomaly", "Partial Functional Dependency", "Multi-valued Dependency",
        "C"
    ),
    (
        141, 11,
        "What is the return value of the C function call: pow(2, 3) when using the standard math library?",
        "6.0", "9.0", "5.0", "8.0",
        "D"
    ),
    (
        142, 11,
        "Which data structure is naturally used by the runtime system to manage recursive function calls?",
        "Call Stack", "Priority Queue", "Circular Queue", "Hash Table",
        "A"
    ),
    (
        143, 11,
        "In the IEEE 754 single-precision floating point standard, how many bits are allocated for the exponent?",
        "7 bits", "8 bits", "11 bits", "23 bits",
        "B"
    ),
    (
        144, 11,
        "Which transport layer protocol provides connectionless and unreliable datagram delivery?",
        "TCP", "SCTP", "UDP", "FTP",
        "C"
    ),
    (
        145, 11,
        "What is the chromatic number of a bipartite graph containing at least one edge?",
        "1", "3", "4", "2",
        "D"
    ),

    # -------------------------------------------------------------
    # GATE PRACTICE QUIZ 2 (Exam ID: 12) - Easy to Moderate (20 Questions)
    # -------------------------------------------------------------
    (
        146, 12,
        "Let A be a 3x3 square matrix whose determinant det(A) = 5. What is the value of det(2A)?",
        "40", "10", "30", "25",
        "A"
    ),
    (
        147, 12,
        "Which of the following is true for the language L = {a^n b^n | n >= 1}?",
        "It is Regular", "It is Context-Free but not Regular", "It is not Context-Free", "It is accepted by DFA",
        "B"
    ),
    (
        148, 12,
        "A system has 4 processes and 6 instances of a single resource type. Each process requires at most 2 resources. Can deadlock occur?",
        "Yes, always", "Depends on execution order", "No, deadlock is impossible", "Deadlock occurs only if preemption is enabled",
        "C"
    ),
    (
        149, 12,
        "In an IPv4 network, what is the default subnet mask for a /26 prefix length?",
        "255.255.255.0", "255.255.255.128", "255.255.255.224", "255.255.255.192",
        "D"
    ),
    (
        150, 12,
        "What is the average case time complexity of QuickSort on an array of n distinct elements?",
        "Theta(n log n)", "Theta(n^2)", "Theta(n)", "Theta(log n)",
        "A"
    ),
    (
        151, 12,
        "Consider a relation R(A, B, C, D) with functional dependencies: AB -> C, C -> D, D -> A. What is the candidate key for R?",
        "C", "AB, BC, BD", "D", "ABC",
        "B"
    ),
    (
        152, 12,
        "A 4-stage pipeline executes an instruction sequence. If the stage delays are 5ns, 7ns, 6ns, and 4ns, what is the clock cycle time?",
        "5 ns", "6 ns", "7 ns", "22 ns",
        "C"
    ),
    (
        153, 12,
        "Which data structure is most suitable for implementing a Breadth-First Search (BFS) on a directed graph?",
        "Stack", "Max-Heap", "Binary Search Tree", "Queue",
        "D"
    ),
    (
        154, 12,
        "If G is a connected planar graph with 10 vertices and 15 edges, how many faces (regions) does its planar representation have?",
        "7", "5", "6", "8",
        "A"
    ),
    (
        155, 12,
        "In Compiler Design, which parsing technique constructs the parse tree from leaves to the root?",
        "Top-Down Parsing", "Bottom-Up Parsing", "Recursive Descent Parsing", "LL(1) Parsing",
        "B"
    ),
    (
        156, 12,
        "What is the minimum Hamming distance between any two valid codewords required to detect up to 3-bit errors?",
        "3", "5", "4", "2",
        "C"
    ),
    (
        157, 12,
        "In C language, what will be the output of: int a=5; printf('%d', a++ + ++a); ?",
        "10", "11", "13", "12",
        "D"
    ),
    (
        158, 12,
        "Which addressing mode specifies the operand within the instruction itself without requiring any memory access?",
        "Immediate Addressing", "Direct Addressing", "Register Indirect Addressing", "Indexed Addressing",
        "A"
    ),
    (
        159, 12,
        "What is the total number of non-isomorphic spanning trees in a complete graph K_4 on 4 labeled vertices (Cayley's formula n^(n-2))?",
        "12", "16", "8", "24",
        "B"
    ),
    (
        160, 12,
        "Which of the following disk scheduling algorithms may cause starvation for requests situated far away from the head?",
        "FCFS", "SCAN", "Shortest Seek Time First (SSTF)", "C-LOOK",
        "C"
    ),
    (
        161, 12,
        "What is the maximum number of keys that can be stored in a 3-level B-tree of order 4 (root is at level 1)?",
        "15", "31", "45", "63",
        "D"
    ),
    (
        162, 12,
        "If a semaphore S is initialized to 10 and 12 wait (P) operations and 5 signal (V) operations are completed, what is the final value of S?",
        "3", "2", "7", "-2",
        "A"
    ),
    (
        163, 12,
        "Which protocol translates human-readable domain names into machine-accessible IP addresses?",
        "ARP", "DNS", "DHCP", "ICMP",
        "B"
    ),
    (
        164, 12,
        "What is the height of an AVL tree with 7 nodes in the worst case (root at height 0)?",
        "1", "2", "3", "4",
        "C"
    ),
    (
        165, 12,
        "In relational algebra, which operation is equivalent to Cartesian Product followed by Selection?",
        "Projection", "Union", "Set Difference", "Theta Join",
        "D"
    ),

    # -------------------------------------------------------------
    # GATE PRACTICE QUIZ 3 (Exam ID: 13) - Moderate (20 Questions)
    # -------------------------------------------------------------
    (
        166, 13,
        "Find the eigenvalues of the matrix A = [[2, 1], [1, 2]].",
        "1 and 3", "2 and 2", "0 and 4", "-1 and 3",
        "A"
    ),
    (
        167, 13,
        "Consider a 5-stage instruction pipeline. 20% of instructions are branch instructions. Each branch incurs 2 stall cycles. What is the speedup over a non-pipelined processor with ideal CPI=1?",
        "4.17", "3.57", "4.80", "5.00",
        "B"
    ),
    (
        168, 13,
        "What is the solution of the recurrence relation T(n) = 2T(n/2) + Theta(n) according to Master Theorem?",
        "Theta(n)", "Theta(n^2)", "Theta(n log n)", "Theta(log n)",
        "C"
    ),
    (
        169, 13,
        "In a direct-mapped cache of size 64 KB with 32-byte block size and 32-bit physical address, how many bits are in the Tag field?",
        "14 bits", "11 bits", "15 bits", "16 bits",
        "D"
    ),
    (
        170, 13,
        "Which of the following grammars is NOT LL(1)?",
        "S -> aS | a", "S -> aA | bB, A -> c, B -> d", "S -> (S) | empty", "S -> aSb | ab",
        "A"
    ),
    (
        171, 13,
        "A virtual memory system has 32-bit virtual addresses, 4 KB page size, and 4-byte page table entries. What is the size of a single-level page table?",
        "2 MB", "4 MB", "1 MB", "8 MB",
        "B"
    ),
    (
        172, 13,
        "Which of the following graph traversal algorithms can detect negative-weight cycles in a directed graph?",
        "Dijkstra's Algorithm", "Prim's Algorithm", "Bellman-Ford Algorithm", "Kruskal's Algorithm",
        "C"
    ),
    (
        173, 13,
        "Let R(A, B, C, D) have FDs: A -> B, B -> C, C -> D, D -> A. In what highest normal form is relation R?",
        "1NF", "2NF", "3NF", "BCNF",
        "D"
    ),
    (
        174, 13,
        "In TCP congestion control, if the congestion window size is 32 KB when a timeout occurs, what is the new slow-start threshold (ssthresh)?",
        "16 KB", "8 KB", "32 KB", "1 KB",
        "A"
    ),
    (
        175, 13,
        "How many edges are present in a maximum bipartite matching graph on K_(m, n)?",
        "m + n", "min(m, n)", "m * n", "max(m, n)",
        "B"
    ),
    (
        176, 13,
        "What is the number of tokens in the following C statement: printf('Sum = %d', x + y); ?",
        "7", "8", "10", "12",
        "C"
    ),
    (
        177, 13,
        "In an operating system using the Buddy System for memory allocation, a request for 55 KB is satisfied with a block of size:",
        "55 KB", "60 KB", "100 KB", "64 KB",
        "D"
    ),
    (
        178, 13,
        "How many distinct binary search trees (BSTs) can be constructed using 4 distinct key values?",
        "14", "24", "42", "10",
        "A"
    ),
    (
        179, 13,
        "Consider the set S = {1, 2, 3, 4, 6, 12} ordered by divisibility. What is the Greatest Lower Bound (GLB) of {4, 6}?",
        "1", "2", "6", "12",
        "B"
    ),
    (
        180, 13,
        "A slotted ALOHA network has a large number of stations generating frames according to Poisson distribution. What is the maximum throughput?",
        "18.4%", "50%", "36.8%", "100%",
        "C"
    ),
    (
        181, 13,
        "In dynamic programming, what is the time complexity to find the optimal Matrix Chain Multiplication of n matrices?",
        "O(n)", "O(n log n)", "O(n^2)", "O(n^3)",
        "D"
    ),
    (
        182, 13,
        "Which of the following relational operations is NOT commutative?",
        "Division", "Natural Join", "Union", "Intersection",
        "A"
    ),
    (
        183, 13,
        "In a synchronous counter with 4 flip-flops, how many distinct states does it cycle through?",
        "8", "16", "32", "4",
        "B"
    ),
    (
        184, 13,
        "For a compiler target architecture with 3-address instructions, what is the minimum number of temporary variables required for: x = a * b + c * d - e / f ?",
        "1", "2", "3", "4",
        "C"
    ),
    (
        185, 13,
        "Which of the following problems is in P (polynomial time solvable)?",
        "Traveling Salesperson Problem", "3-SAT Problem", "Hamiltonian Cycle", "Shortest Path in Directed Graph with non-negative weights",
        "D"
    ),

    # -------------------------------------------------------------
    # GATE PRACTICE QUIZ 4 (Exam ID: 14) - Moderate to Difficult (20 Questions)
    # -------------------------------------------------------------
    (
        186, 14,
        "A 2-way set associative cache has 64 sets, 32 bytes per block, and 32-bit physical address. What are the bit widths of Tag, Set, and Word offset?",
        "Tag=21, Set=6, Word=5", "Tag=20, Set=7, Word=5", "Tag=22, Set=5, Word=5", "Tag=19, Set=8, Word=5",
        "A"
    ),
    (
        187, 14,
        "Let L1 be a context-free language and L2 be a regular language. Which of the following is NOT necessarily context-free?",
        "L1 union L2", "L1 intersect L2_complement", "L1 . L2", "L1*",
        "B"
    ),
    (
        188, 14,
        "A relational database schedule S involves two transactions: T1: R(A), W(A); T2: R(A), W(A), R(B), W(B); T1: R(B), W(B). Is S conflict serializable?",
        "Yes, equivalent to T1 -> T2", "Yes, equivalent to T2 -> T1", "No, it contains a conflict cycle between T1 and T2", "Yes, view serializable only",
        "C"
    ),
    (
        189, 14,
        "In a network with round-trip time RTT = 40 ms and transmission delay = 1 ms per packet, what is the minimum window size for 100% link utilization using Go-Back-N?",
        "21 packets", "40 packets", "80 packets", "41 packets",
        "D"
    ),
    (
        190, 14,
        "What is the maximum number of edges in a simple connected planar bipartite graph on n >= 3 vertices?",
        "2n - 4", "3n - 6", "2n - 2", "n - 1",
        "A"
    ),
    (
        191, 14,
        "Consider a paging system with memory access time of 100 ns and TLB access time of 20 ns. If TLB hit ratio is 90%, what is the Effective Memory Access Time (EMAT)?",
        "120 ns", "130 ns", "140 ns", "220 ns",
        "B"
    ),
    (
        192, 14,
        "What is the asymptotic time complexity of 0/1 Knapsack problem with n items and capacity W using Dynamic Programming?",
        "O(n + W)", "O(n log W)", "O(n * W)", "O(2^n)",
        "C"
    ),
    (
        193, 14,
        "Which of the following grammars generates the language L = {a^i b^j c^k | i = j or j = k}?",
        "Deterministic Context-Free Grammar", "Regular Grammar", "Context-Sensitive only", "Non-Deterministic Context-Free Grammar",
        "D"
    ),
    (
        194, 14,
        "In the Dijkstra shortest-path algorithm using a Fibonacci Heap on a graph with V vertices and E edges, what is the total running time?",
        "O(E + V log V)", "O(V^2)", "O(E log V)", "O(V + E)",
        "A"
    ),
    (
        195, 14,
        "A B+ tree index is created on a search key field of size 12 bytes. Block size is 1024 bytes and block pointer is 8 bytes. What is the maximum order of an internal node?",
        "50", "52", "51", "53",
        "B"
    ),
    (
        196, 14,
        "How many distinct undirected trees can be formed with 5 labeled vertices using Cayley's theorem (n^(n-2))?",
        "25", "60", "125", "256",
        "C"
    ),
    (
        197, 14,
        "In an LR(1) parser, what condition causes a Shift/Reduce conflict in state I on lookahead symbol 'a'?",
        "State has two shifts on 'a'", "State has two reduces on 'a'", "State has neither shift nor reduce", "State has both a shift on 'a' and a reduction [A -> alpha., a]",
        "D"
    ),
    (
        198, 14,
        "If a disc rotates at 7200 RPM, what is the average rotational latency?",
        "4.17 ms", "8.33 ms", "2.08 ms", "6.25 ms",
        "A"
    ),
    (
        199, 14,
        "A system uses Peterson's algorithm for mutual exclusion between two processes P0 and P1. Which flag variable prevents both processes from simultaneously entering the critical section?",
        "turn only", "turn combined with flag array", "flag array only", "hardware lock variable",
        "B"
    ),
    (
        200, 14,
        "What is the number of solutions to x1 + x2 + x3 = 10, where x1, x2, x3 are non-negative integers?",
        "55", "60", "66", "72",
        "C"
    ),
    (
        201, 14,
        "In an IPv4 subnet 192.168.10.0/27, what is the broadcast IP address of this subnet?",
        "192.168.10.255", "192.168.10.63", "192.168.10.32", "192.168.10.31",
        "D"
    ),
    (
        202, 14,
        "In a C program, what does the expression *(ptr + i) evaluate to when ptr points to an integer array?",
        "ptr[i]", "&ptr[i]", "ptr + sizeof(int)*i", "*ptr + i",
        "A"
    ),
    (
        203, 14,
        "What is the maximum number of nodes at depth d in a full m-ary tree (root is at depth 0)?",
        "m*d", "m^d", "d^m", "m^(d+1) - 1",
        "B"
    ),
    (
        204, 14,
        "Which of the following concurrency control protocols is guaranteed to be deadlock-free?",
        "Strict 2-Phase Locking", "Conservative 2-Phase Locking", "Timestamp Ordering Protocol", "Basic 2-Phase Locking",
        "C"
    ),
    (
        205, 14,
        "Which of the following algorithmic paradigms is used by the Floyd-Warshall all-pairs shortest path algorithm?",
        "Greedy Method", "Divide and Conquer", "Backtracking", "Dynamic Programming",
        "D"
    ),

    # -------------------------------------------------------------
    # GATE PRACTICE QUIZ 5 (Exam ID: 15) - Difficult (20 Questions)
    # -------------------------------------------------------------
    (
        206, 15,
        "Which of the following decision problems is DECIDABLE for Context-Free Languages?",
        "Emptiness problem (Is L = empty?)", "Equivalence problem (Is L1 = L2?)", "Universality problem (Is L = Sigma*?)", "Intersection emptiness (Is L1 intersect L2 = empty?)",
        "A"
    ),
    (
        207, 15,
        "In an 8-stage pipeline with clock period 2 ns, a program of 1000 instructions has 100 data hazard stalls and 50 branch penalties (2 cycles each). What is the total execution time?",
        "2200 ns", "2414 ns", "2014 ns", "2600 ns",
        "B"
    ),
    (
        208, 15,
        "A relation R(A, B, C, D, E) has functional dependencies F = {A -> BC, CD -> E, B -> D, E -> A}. Which of the following is a candidate key?",
        "A only", "CD only", "A, E, and BC", "B only",
        "C"
    ),
    (
        209, 15,
        "What is the tightest upper bound for finding the median of an unsorted array of n elements using the Median-of-Medians algorithm?",
        "O(n log n)", "O(n^2)", "O(log n)", "O(n)",
        "D"
    ),
    (
        210, 15,
        "Let G = (V, E) be a directed graph with |V| = n. What is the maximum possible number of strongly connected components in G?",
        "n", "n(n-1)/2", "2^n", "1",
        "A"
    ),
    (
        211, 15,
        "A computer system uses 2-level paging. Logical address is 32 bits, page size is 4 KB, outer page table has 1024 entries, and each entry is 4 bytes. How many bits are for the inner page table index?",
        "12 bits", "10 bits", "8 bits", "14 bits",
        "B"
    ),
    (
        212, 15,
        "In a B+ tree of order 5, what is the minimum number of keys in any non-root internal node?",
        "1", "3", "2", "4",
        "C"
    ),
    (
        213, 15,
        "Which of the following regular expressions correctly denotes the set of all binary strings where every 0 is immediately followed by at least two 1s?",
        "(011)*", "(1 + 01)*", "(011 + 110)*", "(1 + 011)*",
        "D"
    ),
    (
        214, 15,
        "In compiler code optimization, which data-flow analysis framework uses the meet operator 'Union' and is a forward analysis?",
        "Reaching Definitions Analysis", "Available Expressions Analysis", "Live Variable Analysis", "Very Busy Expressions Analysis",
        "A"
    ),
    (
        215, 15,
        "Consider a hash table with 10 slots using open addressing with double hashing: h(k, i) = (h1(k) + i*h2(k)) mod 10 where h1(k) = k mod 10, h2(k) = 1 + (k mod 7). If keys 23, 33, 43 are inserted, at which slot will 43 be placed?",
        "3", "7", "5", "9",
        "B"
    ),
    (
        216, 15,
        "A token bucket traffic shaper has a bucket capacity of 2 MB and token arrival rate of 1 MB/sec. If the maximum transmission burst rate is 5 MB/sec, what is the maximum burst duration?",
        "0.25 seconds", "0.40 seconds", "0.50 seconds", "1.00 seconds",
        "C"
    ),
    (
        217, 15,
        "What is the worst-case number of comparisons made by the optimal comparison-based sorting algorithm to sort 5 elements?",
        "5", "10", "8", "7",
        "D"
    ),
    (
        218, 15,
        "Which of the following problems is Turing-Unrecognizable (Not Recursively Enumerable)?",
        "Complement of Halting Problem (~L_HALT)", "Halting Problem of Turing Machine", "Post Correspondence Problem", "Emptiness of DFA",
        "A"
    ),
    (
        219, 15,
        "In a multi-threaded system, three threads T1, T2, T3 execute on shared variable x initialized to 0. T1: x = x + 1; T2: x = x + 2; T3: x = x * 2. If memory reads and writes are atomic, how many distinct final values can x take?",
        "4", "5", "6", "8",
        "B"
    ),
    (
        220, 15,
        "How many distinct topological orderings exist for a Directed Acyclic Graph (DAG) with vertices {1, 2, 3, 4} and edges {(1, 2), (1, 3), (2, 4), (3, 4)}?",
        "1", "3", "2", "4",
        "C"
    ),
    (
        221, 15,
        "In relational database theory, if every attribute in a relation R is a prime attribute, in which normal form is R guaranteed to be?",
        "1NF only", "2NF only", "BCNF", "3NF",
        "D"
    ),
    (
        222, 15,
        "What is the coefficient of x^12 in the generating function (1 + x^2 + x^4 + x^6 + ...)^3 ?",
        "28", "21", "36", "45",
        "A"
    ),
    (
        223, 15,
        "An asynchronous ripple counter is built using 4 toggle flip-flops each having a propagation delay of 12 ns. What is the maximum clock frequency at which this counter can operate reliably?",
        "25.0 MHz", "20.8 MHz", "15.5 MHz", "10.0 MHz",
        "B"
    ),
    (
        224, 15,
        "Consider Dijkstra algorithm on a graph with V vertices. If negative edge weights are present, which of the following statements is TRUE?",
        "It always loops infinitely", "It always produces the correct answer", "It may terminate with an incorrect shortest path", "It always throws a compilation error",
        "C"
    ),
    (
        225, 15,
        "Which of the following languages is deterministic context-free (DCFL) but its complement is NOT a DCFL?",
        "Equal number of a's and b's", "Palindromes of even length", "a^n b^n c^n", "Every DCFL has a complement that is also DCFL",
        "D"
    )
]
