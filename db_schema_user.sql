/*
DROP TABLE IF EXISTS [user].[WorkApplications];
DROP TABLE IF EXISTS [user].[WorkDescriptions]
DROP TABLE IF EXISTS [user].[CvRags];
DROP TABLE IF EXISTS [user].[CVs];
DROP TABLE IF EXISTS [user].[UserContacts];
DROP TABLE IF EXISTS [user].[Users];
DROP SCHEMA IF EXISTS [user];

CREATE SCHEMA [user];
*/

CREATE TABLE [user].[CVs] (
    [Id]               INT IDENTITY(1,1) PRIMARY KEY,
    [UserId]           INT NOT NULL,

    [Name] NVARCHAR(50) NOT NULL,
    [Note] NVARCHAR(300) NULL,

    [OriginalFileName] NVARCHAR(255) NOT NULL,   -- název při uploadu
    [ContentType]      NVARCHAR(100) NULL,       -- např. application/pdf

    [FileContent]      VARBINARY(MAX) NOT NULL,  -- samotný soubor
    [ExtractedText]    NVARCHAR(MAX) NULL,       -- text pro RAG

    [Active]           BIT NOT NULL DEFAULT 1,   -- pro soft delete

    [CreatedAt]        DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
    [UpdatedAt]        DATETIME2(7) NULL
);

CREATE UNIQUE INDEX UX_CVs_UserId_Name ON [user].[CVs] (UserId, Name);
CREATE UNIQUE INDEX UX_CVs_UserId_OriginalFileName ON [user].[CVs] (UserId, OriginalFileName);


CREATE TABLE [user].[CvRags] (
    [CvId]             INT PRIMARY KEY,
    [RagSettingsJson]  NVARCHAR(MAX) NOT NULL,
    [RagDataJson]      NVARCHAR(MAX) NOT NULL,
    [CreatedAt]        DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
    [UpdatedAt]        DATETIME2(7) NULL,

    CONSTRAINT [FkCvRagsCvs]
        FOREIGN KEY ([CvId]) REFERENCES [user].[CVs]([Id])
        ON DELETE CASCADE
);


CREATE TABLE [user].[Users] (
    [Id]            INT IDENTITY(1,1) PRIMARY KEY,

    [Login]         NVARCHAR(20) NOT NULL,
    [PasswordHash]  NVARCHAR(200) NOT NULL,

    [FirstName]     NVARCHAR(100) NULL,
    [LastName]      NVARCHAR(100) NULL,

    [Active]        BIT NOT NULL DEFAULT 1,

    [CreatedAt]     DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
    [UpdatedAt]     DATETIME2(7) NULL,

    CONSTRAINT UQ_Users_Login UNIQUE ([Login]),
    CONSTRAINT CK_Users_Login_Length CHECK (LEN([Login]) >= 5 AND LEN([Login]) <= 20)
);

CREATE TABLE [user].[UserContacts] (
    [Id]          INT IDENTITY(1,1) PRIMARY KEY,
    [UserId]      INT NOT NULL,

    [Type]        NVARCHAR(20) NOT NULL, 
    [Value]       NVARCHAR(100) NOT NULL,

    [IsPrimary]   BIT NOT NULL DEFAULT 0,
    [Active]      BIT NOT NULL DEFAULT 1,

    [CreatedAt]   DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
    [UpdatedAt]   DATETIME2(7) NULL,

    CONSTRAINT FK_UserContacts_Users
        FOREIGN KEY ([UserId]) REFERENCES [user].[Users]([Id])
);

CREATE UNIQUE INDEX UX_UserContacts_Primary ON [user].[UserContacts] ([UserId], [Type]) WHERE [IsPrimary] = 1 AND [Active] = 1;
ALTER TABLE [user].[UserContacts] ADD CONSTRAINT CK_UserContacts_Type CHECK ([Type] IN ('Email','Phone'));


CREATE TABLE [user].[WorkApplications] (
    [Id]              INT IDENTITY(1,1) PRIMARY KEY,

    [UserId]          INT NOT NULL,
    [WorkId]          INT NOT NULL,
    [CvId]            INT NOT NULL,

    [FirstName]       NVARCHAR(100) NOT NULL,
    [LastName]        NVARCHAR(100) NOT NULL,

    [Email]           NVARCHAR(100) NOT NULL,
    [Phone]           NVARCHAR(100) NOT NULL,

    [Message]         NVARCHAR(1000) NULL,

    [Status]          NVARCHAR(50) NOT NULL DEFAULT 'SUBMITTED',

    [CreatedAt]       DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
    [UpdatedAt]       DATETIME2(7) NULL,

    CONSTRAINT FK_WorkApplications_Users
        FOREIGN KEY ([UserId]) REFERENCES [user].[Users]([Id]),

    CONSTRAINT FK_WorkApplications_CVs
        FOREIGN KEY ([CvId]) REFERENCES [user].[CVs]([Id]),

    CONSTRAINT UQ_WorkApplications_User_Work UNIQUE ([UserId], [WorkId]),
    
    CONSTRAINT CK_WorkApplications_Status
        CHECK ([Status] IN ('SUBMITTED','VIEWED','REJECTED','ACCEPTED'))
);


CREATE TABLE [user].[WorkDescriptions] (
    [UserId]      INT NOT NULL,
    [WorkId]      INT NOT NULL,
    [Description] NVARCHAR(MAX) NOT NULL,
    [UpdatedAt]   DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT PK_WorkDescriptions PRIMARY KEY ([UserId], [WorkId]),

    CONSTRAINT FK_WorkDescriptions_Users
        FOREIGN KEY ([UserId]) REFERENCES [user].[Users]([Id]),

    CONSTRAINT FK_WorkDescriptions_Works
        FOREIGN KEY ([WorkId]) REFERENCES [dbo].[Works]([Id])
);

GO

