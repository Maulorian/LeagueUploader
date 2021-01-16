# League of Legends Match Highlights Uploader
This tool automates the **search**, the **recording** and the **uploading** of *League of Legends* Challenger Games from KR and EU.

The steps of the process are the following:

1. **Retrieves** not yet recorded Challenger Games from database (MongoDB) filled by a worker running: https://github.com/Maulorian/RecordingsEnabler/tree/master.
2. **Processes** those games with the Riot Games API and chooses the **most relevant** player to watch by looking at kills, damages done, etc.
3. **Opens** *League of Legends* and OBS Studio (https://obsproject.com/), **selects** the player, **hides** the fog of war and **records** the game.
4. **Creates** a *5-10 minutes* **highlights video** from a *30-40 minutes game* based off of the a timeline of **events** and their timestamps such as kills, deaths, epic monster kills, etc.
5. **Arranges** the thumbnail for the video based on metadata such as items, kills, runes, etc to be uploaded with the video.
6. **Uploads** on the **Challenger Highlights** *Youtube* Channel: https://www.youtube.com/channel/UCz2zp337iZ9xkpLDACxpRHA
