// ==UserScript==
// @name         AMQ Traning Bot
// @namespace    https://github.com/Terasuki
// @version      1.0
// @description  Sends song data after answer reveal to local server.
// @author       Terasuki
// @match        https://*.animemusicquiz.com/*
// @require      https://raw.githubusercontent.com/TheJoseph98/AMQ-Scripts/master/common/amqScriptInfo.js
// @require      https://raw.githubusercontent.com/TheJoseph98/AMQ-Scripts/master/common/amqWindows.js
// @connect      http://127.0.0.1:8888
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(() => {

    // Do not load on start page.
    if (document.getElementById('startPage')) return;

    // Wait for game to start before starting script.
    let loadInterval = setInterval(() => {
        if (document.getElementById('loadingScreen').classList.contains('hidden')) {
            setup();
            clearInterval(loadInterval);
        }
    }, 500);

    // From: https://github.com/amq-script-project/AMQ-Scripts/blob/master/gameplay/amqAnswerTimesUtility.user.js; exact copy.
    const amqAnswerTimesUtility = new function() {
        this.songStartTime = 0
        this.playerTimes = []
        if (typeof(Listener) === "undefined") {
            return
        }
        new Listener("play next song", () => {
            this.songStartTime = Date.now()
            this.playerTimes = []
        }).bindListener()
        
        new Listener("player answered", (data) => {
            const time = Date.now() - this.songStartTime
            data.forEach(gamePlayerId => {
                this.playerTimes[gamePlayerId] = time
            })
        }).bindListener()
        
        new Listener("Join Game", (data) => {
            const quizState = data.quizState
            if (quizState) {
                this.songStartTime = Date.now() - quizState.songTimer * 1000
            }
        }).bindListener()
    
        new Listener("Spectate Game", (data) => {
            const quizState = data.quizState
            if (quizState) {
                this.songStartTime = Date.now() - quizState.songTimer * 1000
            }
        }).bindListener()
    }()

    function setup() {
    
        new Listener('answer results', (result) => {

            setTimeout(() => {

                let newSong = {
                    gameMode: quiz.gameMode,
                    name: result.songInfo.songName,
                    artist: result.songInfo.artist,
                    anime: result.songInfo.animeNames,
                    annId: result.songInfo.annId,
                    type: result.songInfo.type === 3 ? 'Insert Song' : (result.songInfo.type === 2 ? 'Ending ' + result.songInfo.typeNumber : 'Opening ' + result.songInfo.typeNumber),
                    urls: result.songInfo.urlMap,
                    siteIds: result.songInfo.siteIds,
                    difficulty: typeof result.songInfo.animeDifficulty === 'string' ? 0 : result.songInfo.animeDifficulty.toFixed(1),
                    animeType: result.songInfo.animeType,
                    vintage: result.songInfo.vintage,
                    tags: result.songInfo.animeTags,
                    genre: result.songInfo.animeGenre,
                    altAnswers: [...new Set(result.songInfo.altAnimeNames.concat(result.songInfo.altAnimeNamesAnswers))],
                    startSample: quizVideoController.moePlayers[quizVideoController.currentMoePlayerId].startPoint,
                    videoLength: parseFloat(quizVideoController.moePlayers[quizVideoController.currentMoePlayerId].$player[0].duration.toFixed(2)),
                };
                let findPlayer = Object.values(quiz.players).find((tmpPlayer) => {
                    return tmpPlayer._name === selfName && tmpPlayer.avatarSlot._disabled === false
                });
                if (findPlayer !== undefined) {
                    let playerIdx = Object.values(result.players).findIndex((tmpPlayer) => {
                        return findPlayer.gamePlayerId === tmpPlayer.gamePlayerId
                    });
                    newSong.correct = result.players[playerIdx].correct;
                    newSong.selfAnswer = quiz.players[findPlayer.gamePlayerId].avatarSlot.$answerContainerText.text();
                    newSong.guessTime = amqAnswerTimesUtility.playerTimes[findPlayer.gamePlayerId];
                    newSong.position = result.players[playerIdx].position;
                    newSong.rig_type = result.players[playerIdx].listStatus;
                    newSong.rig_score = (result.players[playerIdx].showScore !== 0 && result.players[playerIdx].showScore !== null) ? result.players[playerIdx].showScore : null;
                }
                GM_xmlhttpRequest({
                    method: 'POST',
                    url: 'http://127.0.0.1:8888',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify(newSong),
                });
            }, 1);

            
        }).bindListener();

    }

    AMQ_addScriptData({
        name: 'AMQ Traning Bot',
        author: 'Terasuki',
        description: `
            <p>Sends song data after answer reveal to local server.</p>
            <p>Thanks to TheJoseph98 for providing window code.</p>
        `
    });
})();
