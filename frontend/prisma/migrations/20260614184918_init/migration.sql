-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL DEFAULT 'user-default',
    "email" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "passwordHash" TEXT NOT NULL,
    "skills" TEXT NOT NULL,
    "preferenceLocation" TEXT,
    "preferenceSalary" INTEGER,
    "preferenceJobType" TEXT,
    "preferenceWorkModel" TEXT,
    "subscriptionStatus" TEXT NOT NULL DEFAULT 'Pro',
    "profileOptimizationScore" INTEGER NOT NULL DEFAULT 0,
    "cvScore" INTEGER,
    "cvRecommendations" TEXT,
    "cvFileName" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Experience" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "company" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "period" TEXT NOT NULL,
    "description" TEXT NOT NULL,

    CONSTRAINT "Experience_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- AddForeignKey
ALTER TABLE "Experience" ADD CONSTRAINT "Experience_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
