import { User, Job, JobApplication } from '../types.js';
import crypto from 'crypto';

// In-memory Database Store
class Database {
  users: Map<string, User & { passwordHash: string }> = new Map();
  jobs: Map<string, Job> = new Map();
  applications: Map<string, JobApplication[]> = new Map(); // key = userId

  constructor() {
    this.seedJobs();
    this.seedDefaultUser();
  }

  // Seed default jobs
  private seedJobs() {
    const seed: Job[] = [
      {
        id: 'job-1',
        title: 'Senior Product Designer',
        company: 'Fintech Solutions Inc.',
        companyLogo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB97tsBSwem3j74eecCB5Kr54qBXSeynr0EzD1bXEENQClaNhejxz8X1Tg8iZ5zWoUHhxh-DTWCIZr8IhCgol1xSY6ysyYGXMsFY57bTBkiN3Y8z5om1hvV_xhtjsSZWfn-wnBHbILpZ2Xj7IhNnRtj_6WfFvpkGM7QS1nq2YWTWL2QFABh5_ejAazho2eY0_r-xupZyXy6a7NN57nvvu3XkGg-71xPGO1bpPnMVnmo2cXbovzNfIrHlt1afadJEmUqxobYa84kVyc',
        location: 'San Francisco, CA (Hybrid)',
        salaryMin: 140,
        salaryMax: 180,
        type: 'Full-time',
        workModel: 'Hybrid',
        description: 'Fintech Solutions is looking for a Senior Product Designer to lead the design of our critical payments and banking workflow portals. You will shape secure, lightning-fast interactions and transform complex financial flows into intuitive steps.',
        responsibilities: [
          'Lead end-to-end design initiatives from initial user mapping to high-fidelity components.',
          'Develop, scale, and maintain our Figma design system libraries and guidelines.',
          'Conduct extensive visual usability testing and directly implement user feedback patterns.',
          'Collaborate closely with product engineering teams to ensure pixel-perfect visual delivery.'
        ],
        requirements: [
          '5+ years of experience designing complex, high-transaction financial or SaaS products.',
          'Expert-level proficiency in Figma, design systems, and rapid prototyping tools.',
          'Outstanding portfolio demonstrating system-level thinking and refined aesthetic judgment.',
          'Skilled in Figma, Design Systems, and cross-functional leadership.'
        ],
        industry: 'FinTech',
        companySize: '100-250 employees',
        website: 'fintechsolutions.co'
      },
      {
        id: 'job-2',
        title: 'UX Engineer',
        company: 'CloudScale Systems',
        companyLogo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB97tsBSwem3j74eecCB5Kr54qBXSeynr0EzD1bXEENQClaNhejxz8X1Tg8iZ5zWoUHhxh-DTWCIZr8IhCgol1xSY6ysyYGXMsFY57bTBkiN3Y8z5om1hvV_xhtjsSZWfn-wnBHbILpZ2Xj7IhNnRtj_6WfFvpkGM7QS1nq2YWTWL2QFABh5_ejAazho2eY0_r-xupZyXy6a7NN57nvvu3XkGg-71xPGO1bpPnMVnmo2cXbovzNfIrHlt1afadJEmUqxobYa84kVyc',
        location: 'Remote (US)',
        salaryMin: 130,
        salaryMax: 160,
        type: 'Full-time',
        workModel: 'Remote',
        description: 'UX Engineers at CloudScale build beautiful client interfaces. You occupy the vital space between design and engineering, translating aesthetic systems into robust Frontend components.',
        responsibilities: [
          'Build, optimize, and maintain reusable UI component libraries using React and Tailwind.',
          'Audit and enhance accessibility structures across core product pages.',
          'Develop reactive dashboards with high-performance animations and flawless user states.',
          'Collaborate with designers to bridge the gap between static design specs and active web files.'
        ],
        requirements: [
          '3+ years of professional experience as a UX Engineer, UI Developer, or React engineer.',
          'Strong command of modern Frontend tech stacks: React, TypeScript, Tailwind CSS, Motion.',
          'Strong familiarity with engineering Figma files and handling asset optimization packages.',
          'Experienced in React, Tailwind CSS, TypeScript, and micro-interactions.'
        ],
        industry: 'Enterprise Software',
        companySize: '50-200 employees',
        website: 'cloudscale.io'
      },
      {
        id: 'job-3',
        title: 'Lead Product Manager',
        company: 'FinTech Solutions Inc.',
        companyLogo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB97tsBSwem3j74eecCB5Kr54qBXSeynr0EzD1bXEENQClaNhejxz8X1Tg8iZ5zWoUHhxh-DTWCIZr8IhCgol1xSY6ysyYGXMsFY57bTBkiN3Y8z5om1hvV_xhtjsSZWfn-wnBHbILpZ2Xj7IhNnRtj_6WfFvpkGM7QS1nq2YWTWL2QFABh5_ejAazho2eY0_r-xupZyXy6a7NN57nvvu3XkGg-71xPGO1bpPnMVnmo2cXbovzNfIrHlt1afadJEmUqxobYa84kVyc',
        location: 'Remote (US)',
        salaryMin: 150,
        salaryMax: 195,
        type: 'Full-time',
        workModel: 'Remote',
        description: 'Lead Product Managers at Fintech Solutions own the key roadmap and growth strategies. You guide agile engineering cycles to build next-generation security and ledger services.',
        responsibilities: [
          'Own the strategic product roadmap for high-frequency banking APIs.',
          'Synthesize quantitative analytics with direct user feedback to identify growth opportunities.',
          'Lead daily agile scrums, grooming backlogs, and crafting perfect specs.',
          'Build close integration partnerships with core retail and merchant platforms.'
        ],
        requirements: [
          '6+ years of product management experience, preferably guiding developer-facing SaaS SDKs.',
          'Deep expertise in Agile methodology, scrum management, and Jira/Linear tooling.',
          'Strong SQL data query skills to synthesize product instrumentation analytics directly.',
          'Skilled in Product Management, Agile Methodology, SQL, and Strategy.'
        ],
        industry: 'FinTech',
        companySize: '100-250 employees',
        website: 'fintechsolutions.co'
      },
      {
        id: 'job-4',
        title: 'Senior PM, Growth',
        company: 'E-Commerce Global',
        companyLogo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB97tsBSwem3j74eecCB5Kr54qBXSeynr0EzD1bXEENQClaNhejxz8X1Tg8iZ5zWoUHhxh-DTWCIZr8IhCgol1xSY6ysyYGXMsFY57bTBkiN3Y8z5om1hvV_xhtjsSZWfn-wnBHbILpZ2Xj7IhNnRtj_6WfFvpkGM7QS1nq2YWTWL2QFABh5_ejAazho2eY0_r-xupZyXy6a7NN57nvvu3XkGg-71xPGO1bpPnMVnmo2cXbovzNfIrHlt1afadJEmUqxobYa84kVyc',
        location: 'New York, NY (On-site)',
        salaryMin: 135,
        salaryMax: 170,
        type: 'Full-time',
        workModel: 'On-site',
        description: 'E-Commerce Global is looking for a Senior Product Manager of Growth to design conversion funnels, onboarding experiments, and payment gateway enhancements to double active merchant registration.',
        responsibilities: [
          'Run rapid A/B testing cycles encompassing entry funnels and onboarding tutorials.',
          'Synthesize merchant analytical paths to remove visual transaction friction points.',
          'Guide cross-functional growth cells involving copywriters, designers, and web developers.',
          'Build, scale, and present key cohort conversion reporting to executives weekly.'
        ],
        requirements: [
          '5+ years as a Growth Product Manager or conversion optimization consultant.',
          'Mastery of web analytics dashboards, A/B testing metrics, and SQL query analysis.',
          'Strong affinity for sleek consumer aesthetics and persuasive interaction design patterns.',
          'A/B Testing, Data Analysis, and Stakeholder Management experience.'
        ],
        industry: 'SaaS',
        companySize: '500+ employees',
        website: 'ecommerceglobal.com'
      },
      {
        id: 'job-5',
        title: 'Product Owner - Core Platform',
        company: 'HealthTech Innovators',
        companyLogo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB97tsBSwem3j74eecCB5Kr54qBXSeynr0EzD1bXEENQClaNhejxz8X1Tg8iZ5zWoUHhxh-DTWCIZr8IhCgol1xSY6ysyYGXMsFY57bTBkiN3Y8z5om1hvV_xhtjsSZWfn-wnBHbILpZ2Xj7IhNnRtj_6WfFvpkGM7QS1nq2YWTWL2QFABh5_ejAazho2eY0_r-xupZyXy6a7NN57nvvu3XkGg-71xPGO1bpPnMVnmo2cXbovzNfIrHlt1afadJEmUqxobYa84kVyc',
        location: 'Boston, MA (Hybrid)',
        salaryMin: 120,
        salaryMax: 150,
        type: 'Full-time',
        workModel: 'Hybrid',
        description: 'HealthTech Innovators is looking for a structured Product Owner to champion agile delivery for clinical dashboard software. You ensure engineers build with HIPAA audits in mind, translating goals into crisp backlog items.',
        responsibilities: [
          'Groom clinician web portal requirements into sprint stories and clear specs.',
          'Coordinate closely with healthcare security compliance cells to secure patient portals.',
          'Remove technical roadblocks for platform engineering sprints during active scrums.',
          'Demo platform feature maps to medical practitioners and advisory boards.'
        ],
        requirements: [
          '3+ years as a Product Owner, Business Analyst, or Scrum Lead in clinical SaaS.',
          'Deep mastery of Agile processes (story point poker, backlog mapping, retro planning).',
          'Passionate about building secure healthcare tools that elevate the primary clinician experience.',
          'Experience in Scrum, Agile Methodology, and Healthcare datasets.'
        ],
        industry: 'Healthcare',
        companySize: '50-120 employees',
        website: 'healthtechinnovators.com'
      }
    ];

    seed.forEach(job => this.jobs.set(job.id, job));
  }

  // Pre-seed a default user Alex Sterling so that the template looks rich and consistent with screenshots!
  private seedDefaultUser() {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync('password123', salt, 1000, 64, 'sha512').toString('hex');
    const passwordHash = `${salt}:${hash}`;

    const defaultUser: User = {
      id: 'user-default',
      email: 'alex.sterling@example.com',
      name: 'Alex Sterling',
      skills: ['Product Management', 'Agile Methodology', 'Data Analysis', 'SQL', 'Figma', 'Stakeholder Management'],
      preferenceLocation: 'San Francisco, CA',
      preferenceSalary: 120, // $120k target minimum
      preferenceJobType: 'Full-time',
      preferenceWorkModel: 'Hybrid',
      subscriptionStatus: 'Pro', // Default to Pro subscriber to show awesome premium features
      experience: [
        {
          id: 'exp-1',
          title: 'Senior Product Manager',
          company: 'TechNova Solutions',
          type: 'Full-time',
          period: 'Jan 2021 - Present • 3 yrs 9 mos',
          description: 'Led the development of the core AI analytics dashboard, increasing user retention by 24%. Managed a cross-functional team of 12 engineers and designers.'
        },
        {
          id: 'exp-2',
          title: 'Product Manager',
          company: 'DataStream Inc',
          type: 'Full-time',
          period: 'Mar 2018 - Dec 2020 • 2 yrs 10 mos',
          description: 'Spearheaded the integration of third-party APIs, streamlining data ingestion for enterprise clients. Conducted extensive user research to refine product roadmap.'
        }
      ],
      profileOptimizationScore: 85,
      cvScore: 85,
      cvRecommendations: [
        "Enrichir la description des expériences professionnelles en quantifiant davantage les résultats opérationnels obtenus (ex: gains de performance, budgets de projet gérés).",
        "Ajouter une section dédiée aux formations et certifications phares liées à la méthodologie Agile pour rassurer l'employeur.",
        "Aérer la structure visuelle globale en améliorant le ratio texte/espace vide pour offrir une expérience de lecture optimale aux recruteurs."
      ],
      cvFileName: "Curriculum_Vitae_Alex_Sterling.pdf"
    };

    this.users.set(defaultUser.id, { ...defaultUser, passwordHash });
    
    // Seed initial application activity for Alex Sterling
    this.applications.set(defaultUser.id, [
      { id: 'app-default-1', jobId: 'job-3', appliedAt: '2026-06-05T10:00:00Z', status: 'applied' },
      { id: 'app-default-2', jobId: 'job-1', appliedAt: '2026-06-04T14:30:00Z', status: 'pending' }
    ]);
  }

  // Utility to hash passwords securely
  hashPassword(password: string): string {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
    return `${salt}:${hash}`;
  }

  // Helper to verify passwords
  verifyPassword(password: string, storedHash: string): boolean {
    const [salt, hash] = storedHash.split(':');
    const verifyHash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
    return verifyHash === hash;
  }
}

export const db = new Database();
