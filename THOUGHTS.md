1. Looking through Spoitfy API right now and dissapointed with how many endpoints they have deprecated
   - Get similar artists could have been a great way to quickly find new artists and create graph based network
2. Can't get around the rate limiting by swapping IP addresses since rate limit is based on client id requests
   - Im still in development mode for this new spotify project and using client id + secret for auth so maxing out at 10 requests per 30s
     - I could get around this by using a better authentication method or spoofing requests so they appear like they are coming from the developer docs page
3. (11M total artists on Spotify)[https://www.searchlogistics.com/learn/statistics/spotify-statistics/#:~:text=and%20Amazon%20Music.-,Spotify%20Artists%20Statistics,and%20creators%20on%20the%20platform.]
4. I initially thought I would just create a random word, search for all albums with that word, then mine the artists of the album and get featured artists on the album
   - I have now realized that the album lookup api calls are gonna be expensive (from rate limiting perspective)
   - I should just use search by artist name (I can get artist stats directly from this api call so dont even need get artists) and use brute force attack
     - Based on some test api calls it seems like 4 character strings will be perfect 36*36*36*36*10 comes out to 16.8M which is similar to our total artists count figure (36 because we need to include numbers and letters, im ignoring special characters in this situation, 10 because average of 10 searches per 4 char string: no idea how accurate this is)
5. I want to use celery / redis / postgres because y'all use a similar stack (based on job posting) - this might be slight overengineering but it said in th eproject description that y'all wanted it to be long running and fault tolerant
6. If I had more time I would dockerize this and also handle crashes better so that if the api / celery / react goes down it is spun back up.
7. I thought about using AWS infra to run this but wanted everything to be local so you could easily spin it up and have full observability / repeatability
8. Rate limiting could be implimented better: instead of just using a hardcoded rate limit ideally it is dynamic and adjusts based on the output of requests from spotify. Having the hard coded value makes it easier when developing because I can set a hardcoded threshold instead of having a dynamic threshold based on request outputs
   - Theres the potential when using dynamic rate limiting that 2 or more requests get executed at the same time and only one request is remaining: this would increase rate limit waiting time more then needed which is why I went with hardcoded value based on experimentats
