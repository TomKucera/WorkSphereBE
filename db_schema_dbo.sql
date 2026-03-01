CREATE TABLE [dbo].[Scans](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Input] [nvarchar](1000) NOT NULL,
	[Output] [nvarchar](max) NULL,
	[StartedAt] [datetime2](7) NOT NULL,
	[EndedAt] [datetime2](7) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

/*
{
    "Id": 5189,
    "Input": "{\"Providers\":[\"StartupJobs\",\"CoolJobs\",\"JobStackIT\",\"Titans\",\"JobsCZ\"]}",
    "Output": "{\"StartupJobs\":{\"AddedOriginalIds\":[],\"RemovedOriginalIds\":[\"100209\",\"100215\",\"100213\",\"100207\",\"100185\",\"100191\",\"100217\"],\"InvalidOriginalIds\":[]},\"CoolJobs\":{\"AddedOriginalIds\":[],\"RemovedOriginalIds\":[],\"InvalidOriginalIds\":[]},\"JobStackIT\":{\"AddedOriginalIds\":[],\"RemovedOriginalIds\":[],\"InvalidOriginalIds\":[]},\"Titans\":{\"AddedOriginalIds\":[],\"RemovedOriginalIds\":[],\"InvalidOriginalIds\":[]},\"JobsCZ\":{\"AddedOriginalIds\":[],\"RemovedOriginalIds\":[\"2000976463\",\"2000944410\",\"2001027170\"],\"InvalidOriginalIds\":[\"2000983203\",\"2001007371\",\"2001039263\"]}}",
    "StartedAt": "2026-02-08T16:02:13.3429239",
    "EndedAt": "2026-02-08T16:04:00.9088465"
  },
*/

CREATE TABLE [dbo].[Works](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Provider] [nvarchar](20) NOT NULL,
	[OriginalId] [nvarchar](50) NOT NULL,
	[Name] [nvarchar](500) NOT NULL,
	[Description] [nvarchar](max) NOT NULL,
	[Url] [nvarchar](500) NOT NULL,
	[Company] [nvarchar](500) NOT NULL,
	[MainArea] [nvarchar](500) NOT NULL,
	[Collaborations] [nvarchar](500) NOT NULL,
	[Areas] [nvarchar](500) NOT NULL,
	[Seniorities] [nvarchar](500) NOT NULL,
	[AddedByScanId] [int] NOT NULL,
	[RemovedByScanId] [int] NULL,
	[ValidFrom] [datetime2](7) GENERATED ALWAYS AS ROW START HIDDEN NOT NULL,
	[ValidTo] [datetime2](7) GENERATED ALWAYS AS ROW END HIDDEN NOT NULL,
	[SnapshotFileName] [nvarchar](50) NULL,
	[RemoteRatio] [int] NULL,
	[SalaryCurrency] [nvarchar](3) NULL,
	[SalaryMax] [int] NULL,
	[SalaryMin] [int] NULL,
	PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

/*
{
    "Id": 24789,
    "Provider": "JobsCZ",
    "OriginalId": "2001004765",
    "Name": "Full-Stack Developer (Java & React)",
    "Description": "",
    "Url": "rpd/2001004765",
    "Company": "PAYMONT, UAB",
    "MainArea": "",
    "Collaborations": "",
    "Areas": "",
    "Seniorities": "",
    "AddedByScanId": 5183,
    "RemovedByScanId": null,
    "SnapshotFileName": null,
    "RemoteRatio": 25,
    "SalaryCurrency": "CZK",
    "SalaryMax": 160000,
    "SalaryMin": 120000
  },
*/