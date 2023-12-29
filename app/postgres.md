postgres
Mxyzptlk1421
database-1.ckn2gtpzltxi.us-east-2.rds.amazonaws.com
5432

=====================
Create database
Choose a database creation method Info
Standard create
You set all of the configuration options, including ones for availability, security, backups, and maintenance.
Easy create
Use recommended best-practice configurations. Some configuration options can be changed after the database is created.
Engine options
Engine typeInfo
Aurora (MySQL Compatible)
Aurora (PostgreSQL Compatible)
MySQL
MariaDB
PostgreSQL
Oracle
Microsoft SQL Server
IBM Db2
Hide filters
Show versions that support the Multi-AZ DB clusterInfo
Create a A Multi-AZ DB cluster with one primary DB instance and two readable standby DB instances. Multi-AZ DB clusters provide up to 2x faster transaction commit latency and automatic failover in typically under 35 seconds.
Engine Version

PostgreSQL 15.4-R3
Templates
Choose a sample template to meet your use case.

Production
Use defaults for high availability and fast, consistent performance.
Dev/Test
This instance is intended for development use outside of a production environment.
Free tier
Use RDS Free Tier to develop new applications, test existing applications, or gain hands-on experience with Amazon RDS. Info
Availability and durability
Deployment optionsInfo
The deployment options below are limited to those supported by the engine you selected above.
Multi-AZ DB Cluster
Creates a DB cluster with a primary DB instance and two readable standby DB instances, with each DB instance in a different Availability Zone (AZ). Provides high availability, data redundancy and increases capacity to serve read workloads.
Multi-AZ DB instance (not supported for Multi-AZ DB cluster snapshot)
Creates a primary DB instance and a standby DB instance in a different AZ. Provides high availability and data redundancy, but the standby DB instance doesn't support connections for read workloads.
Single DB instance (not supported for Multi-AZ DB cluster snapshot)
Creates a single DB instance with no standby DB instances.
Settings
DB instance identifierInfo
Type a name for your DB instance. The name must be unique across all DB instances owned by your AWS account in the current AWS Region.
database-1
The DB instance identifier is case-insensitive, but is stored as all lowercase (as in "mydbinstance"). Constraints: 1 to 60 alphanumeric characters or hyphens. First character must be a letter. Can't contain two consecutive hyphens. Can't end with a hyphen.
Credentials Settings
Master usernameInfo
Type a login ID for the master user of your DB instance.
postgres
1 to 16 alphanumeric characters. The first character must be a letter.
Manage master credentials in AWS Secrets Manager
Manage master user credentials in Secrets Manager. RDS can generate a password for you and manage it throughout its lifecycle.
If you manage the master user credentials in Secrets Manager, some RDS features aren't supported. Learn more 
Auto generate a password
Amazon RDS can generate a password for you, or you can specify your own password.
Master passwordInfo
••••••••••••
Constraints: At least 8 printable ASCII characters. Can't contain any of the following: / (slash), '(single quote), "(double quote) and @ (at sign).
Confirm master passwordInfo
••••••••••••
Instance configuration
The DB instance configuration options below are limited to those supported by the engine that you selected above.

DB instance classInfo
Hide filters
Include previous generation classes
Standard classes (includes m classes)
Memory optimized classes (includes r and x classes)
Burstable classes (includes t classes)

db.t3.micro
2 vCPUs
1 GiB RAM
Network: 2,085 Mbps
Instance Classes
Storage
Storage typeInfo

General Purpose SSD (gp2)
Baseline performance determined by volume size
Allocated storageInfo
20
GiB
The minimum value is 20 GiB and the maximum value is 6,144 GiB
After you modify the storage for a DB instance, the status of the DB instance will be in storage-optimization. Your instance will remain available as the storage-optimization operation completes. Learn more 
Storage autoscaling
Storage autoscalingInfo
Provides dynamic scaling support for your database’s storage based on your application’s needs.
Enable storage autoscaling
Enabling this feature will allow the storage to increase after the specified threshold is exceeded.
Maximum storage thresholdInfo
Charges will apply when your database autoscales to the specified threshold
1000
GiB
The minimum value is 22 GiB and the maximum value is 6,144 GiB
ConnectivityInfo

Compute resource
Choose whether to set up a connection to a compute resource for this database. Setting up a connection will automatically change connectivity settings so that the compute resource can connect to this database.
Don’t connect to an EC2 compute resource
Don’t set up a connection to a compute resource for this database. You can manually set up a connection to a compute resource later.
Connect to an EC2 compute resource
Set up a connection to an EC2 compute resource for this database.
Virtual private cloud (VPC)Info
Choose the VPC. The VPC defines the virtual networking environment for this DB instance.

Default VPC (vpc-e0bd358b)
3 Subnets, 3 Availability Zones
Only VPCs with a corresponding DB subnet group are listed.
After a database is created, you can't change its VPC.
DB subnet groupInfo
Choose the DB subnet group. The DB subnet group defines which subnets and IP ranges the DB instance can use in the VPC that you selected.

default
Public accessInfo
Yes
RDS assigns a public IP address to the database. Amazon EC2 instances and other resources outside of the VPC can connect to your database. Resources inside the VPC can also connect to the database. Choose one or more VPC security groups that specify which resources can connect to the database.
No
RDS doesn't assign a public IP address to the database. Only Amazon EC2 instances and other resources inside the VPC can connect to your database. Choose one or more VPC security groups that specify which resources can connect to the database.
VPC security group (firewall)Info
Choose one or more VPC security groups to allow access to your database. Make sure that the security group rules allow the appropriate incoming traffic.
Choose existing
Choose existing VPC security groups
Create new
Create new VPC security group
Existing VPC security groups

Choose one or more options
default

Availability ZoneInfo

No preference
RDS Proxy
RDS Proxy is a fully managed, highly available database proxy that improves application scalability, resiliency, and security.
Create an RDS ProxyInfo
RDS automatically creates an IAM role and a Secrets Manager secret for the proxy. RDS Proxy has additional costs. For more information, see Amazon RDS Proxy pricing .
Certificate authority - optionalInfo
Using a server certificate provides an extra layer of security by validating that the connection is being made to an Amazon database. It does so by checking the server certificate that is automatically installed on all databases that you provision.

rds-ca-2019 (default)
Expiry: Aug 22, 2024
If you don't select a certificate authority, RDS chooses one for you.
Additional configuration
Database portInfo
TCP/IP port that the database will use for application connections.
5432
Database authentication
Database authentication optionsInfo
Password authentication
Authenticates using database passwords.
Password and IAM database authentication
Authenticates using the database password and user credentials through AWS IAM users and roles.
Password and Kerberos authentication
Choose a directory in which you want to allow authorized users to authenticate with this DB instance using Kerberos Authentication.
Monitoring
Turn on Performance Insights
Retention period for Performance InsightsInfo

7 days (free tier)
AWS KMS keyInfo

(default) aws/rds
Account
824399472754
KMS key ID
alias/aws/rds
You can't change the KMS key after enabling Performance Insights.
Turn on DevOps GuruInfo
DevOps Guru for RDS automatically detects performance anomalies for DB instances and provides recommendations.
Additional configuration
Enhanced Monitoring

Enable Enhanced monitoring
Enabling Enhanced monitoring metrics are useful when you want to see how different processes or threads use the CPU.
Additional configuration
Database options, encryption turned on, backup turned on, backtrack turned off, maintenance, CloudWatch Logs, delete protection turned off.

Estimated Monthly costs
DB instance
13.14 USD
Storage
2.30 USD
Total
15.44 USD
This billing estimate is based on on-demand usage as described in Amazon RDS Pricing . Estimate does not include costs for backup storage, IOs (if applicable), or data transfer.
Estimate your monthly costs for the DB Instance using the AWS Simple Monthly Calculator .
Estimated monthly costs
The Amazon RDS Free Tier is available to you for 12 months. Each calendar month, the free tier will allow you to use the Amazon RDS resources listed below for free:
750 hrs of Amazon RDS in a Single-AZ db.t2.micro, db.t3.micro or db.t4g.micro Instance.
20 GB of General Purpose Storage (SSD).
20 GB for automated backup storage and any user-initiated DB Snapshots.
Learn more about AWS Free Tier. 
When your free usage expires or if your application use exceeds the free usage tiers, you simply pay standard, pay-as-you-go service rates as described in the Amazon RDS Pricing page. 

You are responsible for ensuring that you have all of the necessary rights for any third-party products or services that you use with AWS services.
=====================================================
. Analytics Dashboard APIs
a. Time Filtered Data

Endpoint: /api/analytics/time-filtered
Method: GET
Input:
startTime (query parameter, optional)
endTime (query parameter, optional)
Output: Statistics including total unique users, total calls, and total failures within the specified time range.
Description: Fetches analytics data based on the provided time filter.
b. User Activity Over Time

Endpoint: /api/analytics/user-activity
Method: GET
Input:
startTime (query parameter, optional)
endTime (query parameter, optional)
Output: A time-series data showing the number of users, calls, and failures over the specified time.
Description: Provides data for plotting the activity graph on the dashboard.
c. Logs Data

Endpoint: /api/logs
Method: GET
Input:
startTime (query parameter, optional)
endTime (query parameter, optional)
limit (query parameter, optional, for pagination)
offset (query parameter, optional, for pagination)
Output: A list of logs sorted by timestamp.
Description: Fetches logs for the given time range, useful for displaying in a tabular format on the dashboard.
