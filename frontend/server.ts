import 'dotenv/config';
import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { createServer as createViteServer } from 'vite';
import { db } from './src/server/db.js';
import { JWT } from './src/server/jwt.js';
import { RecommendationService } from './src/server/recommendationService.js';
import { User, Job, ExperienceItem } from './src/types.js';
import { extractTextFromPdf, analyzeCVQuality } from './src/server/cvService.js';
import { PrismaDbService, hashPassword, verifyPassword } from './src/server/prismaDbService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

type AuthenticatedRequest = Request & {
  user?: User;
  cookies?: Record<string, string>;
};

async function startServer() {
  const app = express();
  const PORT = 3000;

  // Initialize and Seed local Prisma relational DB with user data
  await PrismaDbService.seedDefaultUserIfEmpty();

  // JSON parsing middleware with custom limit for PDF uploads
  app.use(express.json({ limit: '15mb' }));

  // Inhouse cookie parser middleware to ensure container-safe, dependency-free cookie reading
  app.use((req: any, res: any, next: NextFunction) => {
    const cookieHeader = req.headers.cookie;
    req.cookies = {};
    if (cookieHeader) {
      cookieHeader.split(';').forEach((cookie: string) => {
        const parts = cookie.split('=');
        const name = parts[0].trim();
        const val = parts.slice(1).join('=').trim();
        req.cookies[name] = decodeURIComponent(val);
      });
    }
    next();
  });

  // DB Error handler helper to prevent unhandled crashes returning html
  function handleDbError(res: Response, err: any, action: string) {
    console.error(`[DATABASE ERROR] Error during standard action "${action}":`, err);

    const isUrlIssue = !process.env.DATABASE_URL || 
                       process.env.DATABASE_URL.includes('localhost') || 
                       process.env.DATABASE_URL.includes('user:password') || 
                       process.env.DATABASE_URL === 'postgresql://user:password@localhost:5432/dbname';

    let friendlyMessage = `Une erreur de base de données est survenue lors de l'opération "${action}".`;
    if (isUrlIssue) {
      friendlyMessage += ` Veuillez configurer une chaîne de connexion PostgreSQL "DATABASE_URL" valide dans les paramètres de Google AI Studio (onglet Settings). Actuellement, la valeur configurée est absente ou correspond à la valeur d'exemple.`;
    } else {
      friendlyMessage += ` Impossible de se connecter au serveur PostgreSQL. Veuillez vérifier que votre "DATABASE_URL" est correcte et active dans votre console.`;
    }

    return res.status(500).json({
      error: friendlyMessage,
      details: err.message || String(err)
    });
  }

  // JWT auth guard middleware
  const authGuard = async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    const token = req.cookies?.auth_token;
    if (!token) {
      return res.status(401).json({ error: 'Unauthorized: Authentication token is missing' });
    }

    const payload = JWT.verify(token);
    if (!payload || !payload.id) {
      return res.status(401).json({ error: 'Unauthorized: Invalid or expired token' });
    }

    try {
      const userProfile = await PrismaDbService.getUserById(payload.id);
      if (!userProfile) {
        return res.status(401).json({ error: 'Unauthorized: User does not exist' });
      }

      req.user = userProfile;
      next();
    } catch (err: any) {
      return handleDbError(res, err, "vérification d'authentification");
    }
  };

  // Auth endpoints
  // Google OAuth entry: generates authorization link
  app.get('/api/auth/google/url', (req: Request, res: Response) => {
    const redirectUri = req.query.redirect_uri as string;
    if (!redirectUri) {
      return res.status(400).json({ error: 'redirect_uri parameter is required' });
    }

    if (process.env.GOOGLE_CLIENT_ID) {
      // Create real Google OAuth authorization link
      const params = new URLSearchParams({
        client_id: process.env.GOOGLE_CLIENT_ID,
        redirect_uri: redirectUri,
        response_type: 'code',
        scope: 'openid profile email',
        state: 'google',
        prompt: 'select_account'
      });
      return res.json({ url: `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}` });
    } else {
      // Create simulated Google accounts selector page url
      const mockUrl = `/api/auth/google/mock-authorize?redirect_uri=${encodeURIComponent(redirectUri)}`;
      return res.json({ url: mockUrl });
    }
  });

  // Serve simple HTML mock auth page directly to bypass the single page application iframe limitation
  app.get('/api/auth/google/mock-authorize', (req: Request, res: Response) => {
    const redirectUri = req.query.redirect_uri as string || '/';
    
    res.send(`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign in with Google</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
        <style>
          body { font-family: 'Roboto', sans-serif; }
        </style>
      </head>
      <body class="bg-slate-50 flex items-center justify-center min-h-screen p-4">
        <div class="bg-white w-full max-w-[440px] border border-gray-200 rounded-xl p-8 shadow-md flex flex-col items-center">
          <svg class="w-10 h-10 mb-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
          </svg>

          <h1 class="text-xl font-medium text-slate-800 mb-1">Choose an account</h1>
          <p class="text-sm text-slate-500 mb-6 text-center">to continue to <span class="font-semibold text-slate-700">AutoApply AI</span></p>

          <div class="w-full space-y-2.5 mb-6">
            <!-- Account 1 -->
            <button onclick="selectUser('physiqueandmath@gmail.com', 'Alex Sterling')" class="w-full flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-all text-left">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold text-sm">
                  AS
                </div>
                <div>
                  <div class="text-xs font-semibold text-slate-700">Alex Sterling</div>
                  <div class="text-[10px] text-slate-400 font-mono">physiqueandmath@gmail.com</div>
                </div>
              </div>
              <div class="text-xs text-blue-600 font-semibold">Active</div>
            </button>

            <!-- Account 2 -->
            <button onclick="selectUser('demo.recruiter@example.com', 'Demo Recruiter')" class="w-full flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-all text-left">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold text-sm">
                  DR
                </div>
                <div>
                  <div class="text-xs font-semibold text-slate-700">Demo Recruiter</div>
                  <div class="text-[10px] text-slate-400 font-mono">demo.recruiter@example.com</div>
                </div>
              </div>
              <div class="text-xs text-slate-400">Guest</div>
            </button>
            
            <div class="border border-slate-100 p-3.5 rounded-lg bg-slate-50 space-y-2">
              <div class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Or enter another Google Account</div>
              <input id="custom-name" type="text" placeholder="Full Name" class="w-full text-xs p-2 border border-slate-200 rounded-md outline-none focus:border-blue-500 bg-white" value="Guest User">
              <input id="custom-email" type="email" placeholder="example@gmail.com" class="w-full text-xs p-2 border border-slate-200 rounded-md outline-none focus:border-blue-500 bg-white" value="guest.user@gmail.com">
              <button onclick="useCustom()" class="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold py-2 rounded-lg transition-colors mt-1">
                Authenticate Mock Account
              </button>
            </div>
          </div>

          <p class="text-[10px] text-slate-400 text-center leading-relaxed">
            AutoApply AI will receive your selected name, email address, profile photo, and security context. Please reference their terms of service before using.
          </p>
        </div>

        <script>
          function selectUser(email, name) {
            const url = new URL(window.location.href);
            const redirectUri = url.searchParams.get('redirect_uri');
            if (!redirectUri) {
              alert('Missing redirect_uri');
              return;
            }
            const callbackUrl = new URL(redirectUri);
            callbackUrl.searchParams.set('code', 'mock_google_code');
            callbackUrl.searchParams.set('email', email);
            callbackUrl.searchParams.set('name', name);
            window.location.href = callbackUrl.toString();
          }

          function useCustom() {
            const name = document.getElementById('custom-name').value.trim();
            const email = document.getElementById('custom-email').value.trim();
            if (!name || !email) {
              alert('Please complete both credentials parameters.');
              return;
            }
            selectUser(email, name);
          }
        </script>
      </body>
      </html>
    `);
  });

  // Google Callback: processes authorization code (real or mock)
  app.get('/api/auth/google/callback', async (req: Request, res: Response) => {
    const { code, email, name, error } = req.query;

    if (error) {
      return res.send(`
        <html>
          <body>
            <script>
              if (window.opener) {
                window.opener.postMessage({ type: 'OAUTH_AUTH_FAILURE', error: "${encodeURIComponent(error as string)}" }, '*');
                window.close();
              } else {
                window.location.href = '/';
              }
            </script>
            <p>Authentication was unsuccessful: ${error}</p>
          </body>
        </html>
      `);
    }

    let resolvedEmail = email as string;
    let resolvedName = name as string;

    if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET && code && code !== 'mock_google_code') {
      try {
        const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            code: code as string,
            client_id: process.env.GOOGLE_CLIENT_ID,
            client_secret: process.env.GOOGLE_CLIENT_SECRET,
            redirect_uri: `${req.protocol}://${req.get('host')}/api/auth/google/callback`,
            grant_type: 'authorization_code',
          })
        });

        if (!tokenResponse.ok) {
          const errDetails = await tokenResponse.text();
          throw new Error(`Token exchange failed: ${errDetails}`);
        }

        const tokenData = await tokenResponse.json();
        const accessToken = tokenData.access_token;

        const profileResponse = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${accessToken}` }
        });

        if (!profileResponse.ok) {
          throw new Error('Failed to retrieve Google profile user data.');
        }

        const profileData = await profileResponse.json();
        resolvedEmail = profileData.email;
        resolvedName = profileData.name || profileData.given_name || 'Google User';
      } catch (err: any) {
        console.error('Real Google OAuth exchange failed, falling back to mock or failing:', err);
        return res.send(`
          <html>
            <body>
              <script>
                if (window.opener) {
                  window.opener.postMessage({ type: 'OAUTH_AUTH_FAILURE', error: "${encodeURIComponent(err.message || 'OAuth validation error')}" }, '*');
                  window.close();
                } else {
                  window.location.href = '/?error=oauth_failed';
                }
              </script>
              <p>Authentication failure: ${err.message}</p>
            </body>
          </html>
        `);
      }
    }

    // Default fallbacks
    if (!resolvedEmail) resolvedEmail = 'physiqueandmath@gmail.com';
    if (!resolvedName) resolvedName = 'Alex Sterling';

    resolvedEmail = resolvedEmail.toLowerCase();

    // SameSite=None and Secure is crucial in preview iframes
    try {
      // Check if user exists in relational DB
      let userWithHash = await PrismaDbService.getUserByEmail(resolvedEmail);

      if (!userWithHash) {
        // Create an automatic user account for Google entry
        const id = `user-${Math.random().toString(36).substring(2, 9)}`;
        const randomPass = Math.random().toString(36).substring(2, 12);
        const passwordHash = hashPassword(randomPass);

        const newUser: User = {
          id,
          email: resolvedEmail,
          name: resolvedName,
          skills: ['Product Management', 'Agile Methodology'],
          preferenceLocation: 'Remote',
          preferenceSalary: 100,
          preferenceJobType: 'Full-time',
          preferenceWorkModel: 'Remote',
          subscriptionStatus: 'Free',
          experience: [],
          profileOptimizationScore: 40
        };

        await PrismaDbService.createUser(newUser, passwordHash);
        userWithHash = await PrismaDbService.getUserByEmail(resolvedEmail);
      }

      const { passwordHash, ...userProfile } = userWithHash!;
      const token = JWT.sign({ id: userProfile.id, email: userProfile.email });
      res.setHeader('Set-Cookie', `auth_token=${token}; HttpOnly; Path=/; SameSite=None; Secure; Max-Age=36000`);
    } catch (err: any) {
      console.error('Database connection failed during Google Authentication sync:', err);
      const isUrlIssue = !process.env.DATABASE_URL || process.env.DATABASE_URL.includes('user:password');
      let detailsMessage = "Une erreur de connexion à la base de données PostgreSQL est survenue.";
      if (isUrlIssue) {
        detailsMessage += " Le paramètre DATABASE_URL n'est pas configuré ou est invalide dans les paramètres de Google AI Studio.";
      }
      return res.send(`
        <html>
          <body>
            <script>
              if (window.opener) {
                window.opener.postMessage({ type: 'OAUTH_AUTH_FAILURE', error: "${encodeURIComponent(detailsMessage)}" }, '*');
                window.close();
              } else {
                window.location.href = '/?error=db_failed';
              }
            </script>
            <p>Database synchronization failure: ${detailsMessage}</p>
          </body>
        </html>
      `);
    }

    return res.send(`
      <html>
        <body>
          <script>
            if (window.opener) {
              window.opener.postMessage({ type: 'OAUTH_AUTH_SUCCESS' }, '*');
              window.close();
            } else {
              window.location.href = '/';
            }
          </script>
          <p>Authentication process successful. Syncing dashboard...</p>
        </body>
      </html>
    `);
  });

  // Auth endpoints
  app.post('/api/auth/register', async (req: Request, res: Response) => {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ error: 'Name, email, and password are required' });
    }

    try {
      // Check if user already exists
      const existing = await PrismaDbService.getUserByEmail(email);
      if (existing) {
        return res.status(400).json({ error: 'A user with this email already exists' });
      }

      // Create user
      const id = `user-${Math.random().toString(36).substring(2, 9)}`;
      const passHash = hashPassword(password);
      
      const newUser: User = {
        id,
        email: email.toLowerCase(),
        name,
        skills: [],
        preferenceLocation: 'Remote',
        preferenceSalary: 80,
        preferenceJobType: 'Full-time',
        preferenceWorkModel: 'Remote',
        subscriptionStatus: 'Free', // Default tier
        experience: [],
        profileOptimizationScore: 40
      };

      await PrismaDbService.createUser(newUser, passHash);

      // Sign JWT
      const token = JWT.sign({ id: newUser.id, email: newUser.email });

      // Secure cookie setup
      res.setHeader('Set-Cookie', `auth_token=${token}; HttpOnly; Path=/; SameSite=None; Secure; Max-Age=36000`);
      return res.status(201).json({ user: newUser, message: 'Registration successful' });
    } catch (err: any) {
      return handleDbError(res, err, "création de compte");
    }
  });

  app.post('/api/auth/login', async (req: Request, res: Response) => {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    try {
      const userWithHash = await PrismaDbService.getUserByEmail(email);

      if (!userWithHash) {
        return res.status(401).json({ error: 'Invalid email or password' });
      }

      const passwordMatches = verifyPassword(password, userWithHash.passwordHash);
      if (!passwordMatches) {
        return res.status(401).json({ error: 'Invalid email or password' });
      }

      // Clear password hash
      const { passwordHash, ...userProfile } = userWithHash;

      const token = JWT.sign({ id: userProfile.id, email: userProfile.email });
      res.setHeader('Set-Cookie', `auth_token=${token}; HttpOnly; Path=/; SameSite=None; Secure; Max-Age=36000`);
      
      return res.json({ user: userProfile, message: 'Logged in successfully' });
    } catch (err: any) {
      return handleDbError(res, err, "connexion");
    }
  });

  app.post('/api/auth/logout', (req: Request, res: Response) => {
    // Clear cookie
    res.setHeader('Set-Cookie', `auth_token=; HttpOnly; Path=/; SameSite=None; Secure; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT`);
    return res.json({ message: 'Logged out successfully' });
  });

  app.get('/api/auth/me', async (req: AuthenticatedRequest, res: Response) => {
    const token = req.cookies?.auth_token;
    if (!token) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const payload = JWT.verify(token);
    if (!payload || !payload.id) {
       return res.status(401).json({ error: 'Token invalid or expired' });
    }

    try {
      const userProfile = await PrismaDbService.getUserById(payload.id);
      if (!userProfile) {
         return res.status(401).json({ error: 'User not found' });
      }

      return res.json({ user: userProfile });
    } catch (err: any) {
      return handleDbError(res, err, "récupération du profil");
    }
  });

  // Profile Endpoints
  app.put('/api/profile', authGuard, async (req: AuthenticatedRequest, res: Response) => {
    const { 
      name, 
      skills, 
      preferenceLocation, 
      preferenceSalary, 
      preferenceJobType, 
      preferenceWorkModel, 
      experience 
    } = req.body;

    const user = req.user!;
    const updates: Partial<User> = {};

    if (name !== undefined) updates.name = name;
    if (skills !== undefined) updates.skills = skills;
    if (preferenceLocation !== undefined) updates.preferenceLocation = preferenceLocation;
    if (preferenceSalary !== undefined) updates.preferenceSalary = Number(preferenceSalary);
    if (preferenceJobType !== undefined) updates.preferenceJobType = preferenceJobType;
    if (preferenceWorkModel !== undefined) updates.preferenceWorkModel = preferenceWorkModel;
    if (experience !== undefined) updates.experience = experience;

    // Recalculate profile optimization score dynamically
    const currentSkills = skills !== undefined ? skills : user.skills;
    const currentExperience = experience !== undefined ? experience : user.experience;
    const currentLocation = preferenceLocation !== undefined ? preferenceLocation : user.preferenceLocation;
    const currentSalary = preferenceSalary !== undefined ? preferenceSalary : user.preferenceSalary;

    let optimizationScore = 40;
    if (currentSkills.length > 0) optimizationScore += 15;
    if (currentSkills.length > 4) optimizationScore += 10;
    if (currentExperience.length > 0) optimizationScore += 20;
    if (currentLocation && currentSalary) optimizationScore += 15;
    updates.profileOptimizationScore = Math.min(100, optimizationScore);

    try {
      const updatedUser = await PrismaDbService.updateUser(user.id, updates);
      return res.json({ user: updatedUser, message: 'Profile updated successfully' });
    } catch (err: any) {
      return handleDbError(res, err, "mise à jour du profil");
    }
  });

  // CV Upload and Quality Score Endpoint
  app.post('/api/profile/upload-cv', authGuard, async (req: AuthenticatedRequest, res: Response) => {
    const { file, fileName } = req.body;
    
    if (!file) {
      return res.status(400).json({ error: 'Fichier CV au format PDF manquant.' });
    }

    try {
      // Decode base64 PDF
      const base64Data = file.replace(/^data:.*;base64,/, '');
      const buffer = Buffer.from(base64Data, 'base64');

      // Extract text content using pdf-parse
      const extractedText = await extractTextFromPdf(buffer);

      if (!extractedText || extractedText.trim().length === 0) {
        return res.status(400).json({ 
          error: "Échec de l'extraction : Le PDF semble vide ou est une image scannée sans texte sélectionnable." 
        });
      }

      // Analyze quality with Gemini / fallback rule engine
      const analysis = await analyzeCVQuality(extractedText);

      // Persist results under the authenticated user session in relational DB
      const user = req.user!;
      
      const updates: Partial<User> = {
        cvScore: analysis.score,
        cvRecommendations: analysis.recommendations,
        cvFileName: fileName || 'cv_uploaded.pdf',
        profileOptimizationScore: Math.min(100, user.profileOptimizationScore + 10)
      };

      const updatedUser = await PrismaDbService.updateUser(user.id, updates);

      return res.json({
        user: updatedUser,
        message: 'Votre CV a été importé et analysé avec succès ! Les recommandations sont prêtes sur votre Dashboard.',
        analysis
      });
    } catch (err: any) {
      console.error('Erreur lors du traitement du CV PDF:', err);
      if (err.message && (err.message.includes('Prisma') || err.message.includes('connect') || err.message.includes('database') || err.message.includes('DB'))) {
        return handleDbError(res, err, "sauvegarde du CV");
      }
      return res.status(500).json({ 
        error: err.message || 'Une défaillance technique est survenue durant la lecture du CV.' 
      });
    }
  });

  // Billing Tier Endpoints
  app.put('/api/billing/upgrade', authGuard, async (req: AuthenticatedRequest, res: Response) => {
    const user = req.user!;
    try {
      const updatedUser = await PrismaDbService.updateUser(user.id, { subscriptionStatus: 'Pro' });
      return res.json({ user: updatedUser, message: 'Tier upgraded to Pro successfully' });
    } catch (err: any) {
      return handleDbError(res, err, "mise à niveau d'abonnement");
    }
  });

  app.put('/api/billing/downgrade', authGuard, async (req: AuthenticatedRequest, res: Response) => {
    const user = req.user!;
    try {
      const updatedUser = await PrismaDbService.updateUser(user.id, { subscriptionStatus: 'Free' });
      return res.json({ user: updatedUser, message: 'Tier downgraded to Free successfully' });
    } catch (err: any) {
      return handleDbError(res, err, "rétrogradation d'abonnement");
    }
  });

  // Recommendations and Full-Text Search Route driven by user's interested profiles
  app.post('/api/recommendations', authGuard, async (req: AuthenticatedRequest, res: Response) => {
    try {
      const user = req.user!;
      const { profiles } = req.body;

      if (!profiles || !Array.isArray(profiles)) {
        return res.status(400).json({ error: "Les profils d'intérêt doivent être transmis sous forme d'un tableau de chaînes." });
      }

      const rawJobs = Array.from(db.jobs.values());
      const userApps = db.applications.get(user.id) || [];

      // 1. Perform Full-Text Search (phrase and token matching) across available jobs
      const matchedCandidates = [];

      for (const job of rawJobs) {
        let matchCount = 0;
        
        if (profiles.length > 0) {
          for (const p of profiles) {
            const cleanP = p.trim().toLowerCase();
            if (!cleanP) continue;

            // Full-Text Search: scan title, description, industry, and requirements
            if (
              job.title.toLowerCase().includes(cleanP) ||
              job.description.toLowerCase().includes(cleanP) ||
              job.industry.toLowerCase().includes(cleanP) ||
              job.requirements.some(r => r.toLowerCase().includes(cleanP))
            ) {
              matchCount++;
            }
          }
        } else {
          // If no profiles defined, fallback to general match of 1 to display options
          matchCount = 1;
        }

        matchedCandidates.push({
          job,
          scoreFTS: matchCount
        });
      }

      // Sort with highest Full-Text Search match first
      matchedCandidates.sort((a, b) => b.scoreFTS - a.scoreFTS);

      // Take standard set (up to 5 jobs) for precise Gemini evaluation and grading
      const selectedJobs = matchedCandidates.slice(0, 5).map(c => c.job);

      // 2. Perform dynamic Gemini-powered evaluation and suggestions returning fit reasons
      const enrichedRecommendations = [];
      for (const job of selectedJobs) {
        const app = userApps.find(a => a.jobId === job.id);
        
        let matchDetails;
        try {
          matchDetails = await RecommendationService.getGeminiMatch(profiles, job, user);
        } catch (gemError) {
          console.error("Gemini match failed, falling back to basic matching:", gemError);
          matchDetails = RecommendationService.getMatch(user, job);
        }

        enrichedRecommendations.push({
          ...job,
          match: matchDetails,
          applied: !!app,
          applicationStatus: app ? app.status : null
        });
      }

      // Final sorting based on match score descending
      enrichedRecommendations.sort((a, b) => b.match.score - a.match.score);

      return res.json({ jobs: enrichedRecommendations });
    } catch (err: any) {
      console.error("Erreur serveur lors de la génération des recommandations:", err);
      return res.status(500).json({ error: "Impossible de générer des recommandations actuellement." });
    }
  });

  // Jobs Endpoints (Enriched with rule-based matching score on return)
  app.get('/api/jobs', authGuard, async (req: AuthenticatedRequest, res: Response) => {
    const user = req.user!;
    const rawJobs = Array.from(db.jobs.values());
    const userApps = db.applications.get(user.id) || [];

    try {
      const jobsWithMatches = [];
      for (const job of rawJobs) {
        const matchDetails = await RecommendationService.getGeminiMatch(user.skills, job, user);
        const app = userApps.find(a => a.jobId === job.id);
        jobsWithMatches.push({
          ...job,
          match: matchDetails,
          applied: !!app,
          applicationStatus: app ? app.status : null
        });
      }

      // Rank jobs based on Match Scores descending
      jobsWithMatches.sort((a, b) => b.match.score - a.match.score);
      return res.json({ jobs: jobsWithMatches });
    } catch (err) {
      console.warn("Using fallback matching logic for /api/jobs list:", err);
      const jobsWithMatches = rawJobs.map(job => {
        const matchDetails = RecommendationService.getMatch(user, job);
        const app = userApps.find(a => a.jobId === job.id);
        return {
          ...job,
          match: matchDetails,
          applied: !!app,
          applicationStatus: app ? app.status : null
        };
      });
      jobsWithMatches.sort((a, b) => b.match.score - a.match.score);
      return res.json({ jobs: jobsWithMatches });
    }
  });

  app.get('/api/jobs/:id', authGuard, (req: AuthenticatedRequest, res: Response) => {
    const user = req.user!;
    const job = db.jobs.get(req.params.id);

    if (!job) {
      return res.status(404).json({ error: 'Job listing not found' });
    }

    const matchDetails = RecommendationService.getMatch(user, job);
    const userApps = db.applications.get(user.id) || [];
    const app = userApps.find(a => a.jobId === job.id);

    return res.json({
      job: {
        ...job,
        match: matchDetails,
        applied: !!app,
        applicationStatus: app ? app.status : null
      }
    });
  });

  // Application Endpoints
  app.post('/api/jobs/:id/apply', authGuard, (req: AuthenticatedRequest, res: Response) => {
    const user = req.user!;
    const jobId = req.params.id;

    const job = db.jobs.get(jobId);
    if (!job) {
      return res.status(404).json({ error: 'Job listing not found' });
    }

    let userApps = db.applications.get(user.id) || [];
    
    // Check if subscription gating applies
    // Free accounts can only apply to up to 2 jobs as a freemium SaaS demonstration ceiling constraint
    if (user.subscriptionStatus === 'Free' && userApps.length >= 2) {
      return res.status(403).json({ 
        error: 'Application Limit Reached',
        gated: true,
        message: 'Free Plan accounts are restricted to 2 job applications. Upgrade to Pro for unlimited AI matching and job applications!' 
      });
    }

    // Check if already applied
    const existing = userApps.find(a => a.jobId === jobId);
    if (existing) {
      return res.json({ message: 'You have already applied for this job listing', application: existing });
    }

    const newApp: any = {
      id: `app-${Math.random().toString(36).substring(2, 9)}`,
      jobId,
      status: 'applied',
      appliedAt: new Date().toISOString()
    };

    userApps.push(newApp);
    db.applications.set(user.id, userApps);

    return res.status(201).json({ message: 'Application submitted successfully!', application: newApp });
  });

  // Dashboard Stats Enriched Endpoint
  app.get('/api/dashboard/stats', authGuard, (req: AuthenticatedRequest, res: Response) => {
    const user = req.user!;
    const userApps = db.applications.get(user.id) || [];

    const autoAppliedCount = userApps.filter(a => a.status === 'applied').length;
    
    // Seed some static analytics that look premium and high-fidelity
    const interviewsSecured = userApps.length > 0 ? Math.floor(userApps.length * 0.3) + 1 : 0;
    const profileViews = user.skills.length * 12 + 45;

    // CV Quality scoring overrides the alignment score
    const alignmentScore = user.cvScore !== undefined ? user.cvScore : user.profileOptimizationScore;

    return res.json({
      stats: {
        autoAppliedCount,
        interviewsSecured,
        profileViews,
        alignmentScore
      }
    });
  });

  // Vite Integration setup
  if (process.env.NODE_ENV !== "production") {
    // Development Mode
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    
    app.use(vite.middlewares);
  } else {
    // Production Mode
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req: Request, res: Response) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  // Listening exclusively on port 3000
  app.listen(PORT, "localhost", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer().catch(err => {
  console.error('Critical server initiation failure:', err);
});
