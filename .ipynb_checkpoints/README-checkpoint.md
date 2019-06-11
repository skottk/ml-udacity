# MLAI classroom work on harvesting data extract.

# Project goal
We are experimenting with identifying content harvesting behavior from transaction logs.

# Data
We have a sample of data collected from raw transaction logs as follows:
- Select {begin time, end time} for a full session of data of a known attacker in operation
- Collect _all_ transaction data for an hour-to-hour time interval containing the attack session
  - E.g., if the attacker acted from 12:13PM to 1:48PM, collect 12:00PM to 2:00PM
- Repeat
 
# Challenges
- The data contains many, many user sessions that are interleaved
- There are ~1000 user transaction entries for every attack entry
- The data is sequenced, meaning that each log entry is essentially meaningless for inferring intent; we have to look at the entire session in order to distinguish attacks from ordinary usage.

# Data preparation
We will vectorize session data into single rows, transforming a collection of log entries for many users into a collection of row-per-session. Each row includes a column for each transaction type, which will contain the count of that transaction type over the course of that session.
There's a useful analogy to the bag-of-words approach for text processing.

## Out of scope
- We will make no attempt to capture sequence behaviors using LSTM/LCS methods
- There are obvious tells we are aware of, such as the attacker using a particular query string that ordinary users rarely employ. We are not going to attempt to capture these at this time.

