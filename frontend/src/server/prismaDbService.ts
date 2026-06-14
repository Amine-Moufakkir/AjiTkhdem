import { prisma } from './prisma.ts';
import { User, ExperienceItem } from '../types.js';
import crypto from 'crypto';

// Password hashing helper (copied alignment from db.ts)
export function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
  return `${salt}:${hash}`;
}

export function verifyPassword(password: string, storedHash: string): boolean {
  if (!storedHash || !storedHash.includes(':')) return false;
  const [salt, hash] = storedHash.split(':');
  const verifyHash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
  return verifyHash === hash;
}

// Convert Prisma User + Experience model to standard User type
export function mapPrismaToUser(prismaUser: any): User {
  let skills: string[] = [];
  try {
    skills = JSON.parse(prismaUser.skills || '[]');
  } catch {
    skills = prismaUser.skills ? prismaUser.skills.split(',').filter(Boolean) : [];
  }

  let cvRecommendations: string[] = [];
  try {
    cvRecommendations = JSON.parse(prismaUser.cvRecommendations || '[]');
  } catch {
    cvRecommendations = prismaUser.cvRecommendations ? JSON.parse(prismaUser.cvRecommendations) : [];
  }

  const experience: ExperienceItem[] = (prismaUser.experiences || []).map((exp: any) => ({
    id: exp.id,
    title: exp.title,
    company: exp.company,
    type: exp.type,
    period: exp.period,
    description: exp.description
  }));

  return {
    id: prismaUser.id,
    email: prismaUser.email,
    name: prismaUser.name,
    skills,
    preferenceLocation: prismaUser.preferenceLocation || 'Remote',
    preferenceSalary: prismaUser.preferenceSalary || 80,
    preferenceJobType: (prismaUser.preferenceJobType || 'Full-time') as any,
    preferenceWorkModel: (prismaUser.preferenceWorkModel || 'Remote') as any,
    subscriptionStatus: (prismaUser.subscriptionStatus || 'Free') as any,
    experience,
    profileOptimizationScore: prismaUser.profileOptimizationScore,
    cvScore: prismaUser.cvScore !== null ? prismaUser.cvScore : undefined,
    cvRecommendations: cvRecommendations.length > 0 ? cvRecommendations : undefined,
    cvFileName: prismaUser.cvFileName !== null ? prismaUser.cvFileName : undefined
  };
}

export class PrismaDbService {
  static async getUserById(id: string): Promise<User | null> {
    try {
      const prismaUser = await prisma.user.findUnique({
        where: { id },
        include: { experiences: true }
      });
      if (!prismaUser) return null;
      return mapPrismaToUser(prismaUser);
    } catch (err) {
      console.error(`Error querying user ID ${id}:`, err);
      return null;
    }
  }

  static async getUserByEmail(email: string): Promise<(User & { passwordHash: string }) | null> {
    try {
      const prismaUser = await prisma.user.findFirst({
        where: { email: email.toLowerCase() },
        include: { experiences: true }
      });
      if (!prismaUser) return null;
      const user = mapPrismaToUser(prismaUser);
      return {
        ...user,
        passwordHash: prismaUser.passwordHash
      };
    } catch (err) {
      console.error(`Error querying user by email ${email}:`, err);
      return null;
    }
  }

  static async createUser(userData: User, passwordHash: string): Promise<User> {
    try {
      const prismaUser = await prisma.user.create({
        data: {
          id: userData.id,
          email: userData.email.toLowerCase(),
          name: userData.name,
          passwordHash,
          skills: JSON.stringify(userData.skills || []),
          preferenceLocation: userData.preferenceLocation,
          preferenceSalary: userData.preferenceSalary,
          preferenceJobType: userData.preferenceJobType,
          preferenceWorkModel: userData.preferenceWorkModel,
          subscriptionStatus: userData.subscriptionStatus,
          profileOptimizationScore: userData.profileOptimizationScore,
          cvScore: userData.cvScore,
          cvRecommendations: userData.cvRecommendations ? JSON.stringify(userData.cvRecommendations) : null,
          cvFileName: userData.cvFileName,
          experiences: {
            create: (userData.experience || []).map(exp => ({
              id: exp.id,
              title: exp.title,
              company: exp.company,
              type: exp.type,
              period: exp.period,
              description: exp.description
            }))
          }
        },
        include: { experiences: true }
      });
      return mapPrismaToUser(prismaUser);
    } catch (err) {
      console.error("Error creating user in Prisma:", err);
      throw err;
    }
  }

  static async updateUser(id: string, updates: Partial<User>): Promise<User> {
    try {
      const dataToUpdate: any = {};
      if (updates.name !== undefined) dataToUpdate.name = updates.name;
      if (updates.email !== undefined) dataToUpdate.email = updates.email.toLowerCase();
      if (updates.skills !== undefined) dataToUpdate.skills = JSON.stringify(updates.skills);
      if (updates.preferenceLocation !== undefined) dataToUpdate.preferenceLocation = updates.preferenceLocation;
      if (updates.preferenceSalary !== undefined) dataToUpdate.preferenceSalary = updates.preferenceSalary;
      if (updates.preferenceJobType !== undefined) dataToUpdate.preferenceJobType = updates.preferenceJobType;
      if (updates.preferenceWorkModel !== undefined) dataToUpdate.preferenceWorkModel = updates.preferenceWorkModel;
      if (updates.subscriptionStatus !== undefined) dataToUpdate.subscriptionStatus = updates.subscriptionStatus;
      if (updates.profileOptimizationScore !== undefined) dataToUpdate.profileOptimizationScore = updates.profileOptimizationScore;
      if (updates.cvScore !== undefined) dataToUpdate.cvScore = updates.cvScore;
      if (updates.cvRecommendations !== undefined) dataToUpdate.cvRecommendations = JSON.stringify(updates.cvRecommendations);
      if (updates.cvFileName !== undefined) dataToUpdate.cvFileName = updates.cvFileName;

      // Handle experiences update as a transaction/relation replacement if experiences exist in update parameters
      if (updates.experience !== undefined) {
        await prisma.$transaction([
          // delete existing experiences for user first
          prisma.experience.deleteMany({ where: { userId: id } }),
          // insert new experiences
          prisma.experience.createMany({
            data: updates.experience.map(exp => ({
              id: exp.id,
              userId: id,
              title: exp.title,
              company: exp.company,
              type: exp.type,
              period: exp.period,
              description: exp.description
            }))
          })
        ]);
      }

      // Perform user fields update
      const updatedPrismaUser = await prisma.user.update({
        where: { id },
        data: dataToUpdate,
        include: { experiences: true }
      });

      return mapPrismaToUser(updatedPrismaUser);
    } catch (err) {
      console.error(`Error updating user ${id}:`, err);
      throw err;
    }
  }

  // Pre-seeds Default User Alex Sterling (exactly same content as db.ts)
  static async seedDefaultUserIfEmpty() {
    try {
      const count = await prisma.user.count();
      if (count > 0) {
        console.log("Database already contains users. Skipping pre-seed.");
        return;
      }

      console.log("Seeding default user 'Alex Sterling' in Prisma database...");
      
      const defaultPassHash = hashPassword('password123');
      const defaultUser: User = {
        id: 'user-default',
        email: 'alex.sterling@example.com',
        name: 'Alex Sterling',
        skills: ['Product Management', 'Agile Methodology', 'Data Analysis', 'SQL', 'Figma', 'Stakeholder Management'],
        preferenceLocation: 'San Francisco, CA',
        preferenceSalary: 120,
        preferenceJobType: 'Full-time',
        preferenceWorkModel: 'Hybrid',
        subscriptionStatus: 'Pro',
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
        cvFileName: 'Curriculum_Vitae_Alex_Sterling.pdf'
      };

      await this.createUser(defaultUser, defaultPassHash);
      console.log("Pre-seed completed successfully in PostgreSQL database via Prisma.");
    } catch (err) {
      console.error("Failed to seed default user in Prisma:", err);
    }
  }
}
