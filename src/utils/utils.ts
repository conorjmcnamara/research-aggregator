export interface dbDataI {
    topic: string;
    title: string;
    date: string;
    abstract: string;
    url: string;
    source: string;
    authors: string[];
}

export interface showHiddenI {
    [id: string]: boolean
}

export interface topicsI {
    [id: string]: string
};

export const topics: topicsI = {
    "AI": "Artificial Intelligence",
    "CC": "Computational Complexity",
    "CE": "Computational Engineering, Finance, and Science",
    "CG": "Computational Geometry",
    "CL": "Computation and Language",
    "CR": "Cryptography and Security",
    "CV": "Computer Vision and Pattern Recognition",
    "CY": "Computers and Society",
    "DB": "Databases",
    "DC": "Distributed, Parallel, and Cluster Computing",
    "DL": "Digital Libraries",
    "DM": "Discrete Mathematics",
    "DS": "Data Structures and Algorithms",
    "ET": "Emerging Technologies",
    "FL": "Formal Languages and Automata Theory",
    "GT": "Game Theory",
    "GL": "General Literature",
    "GR": "Graphics",
    "AR": "Hardware Architecture",
    "HC": "Human-Computer Interaction", 
    "IR": "Information Retrieval",
    "IT": "Information Theory",
    "LG": "Machine Learning",
    "LO": "Logic in Computer Science",
    "MA": "Multiagent Systems",
    "MM": "Multimedia",
    "MS": "Mathematical Software",
    "NA": "Numerical Analysis",
    "NE": "Neural and Evolutionary Computing",
    "NI": "Networking and Internet Architecture",
    "OH": "Other",
    "OS": "Operating Systems",
    "PF": "Performance",
    "PL": "Programming Languages",
    "RO": "Robotics",
    "SC": "Symbolic Computation",
    "SD": "Sound",
    "SE": "Software Engineering",
    "SI": "Social and Information Networks",
    "SY": "Systems and Control"
};