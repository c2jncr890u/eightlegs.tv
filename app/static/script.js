function skip()
{   
    window.location = "/player?q="+encodeURIComponent(document.getElementById("q").value);
}
function maybeskip()
{
    if(ytplayer.getPlayerState()==0) skip();
}
function onYouTubePlayerReady(playerid)
{
    var ytplayer = document.getElementById("ytplayer");
    ytplayer.addEventListener("onError", "skip" );
    ytplayer.addEventListener("onStateChange", "maybeskip" );
}
function rate( rating ){
    var v = new RegExp("[\\?&]v=([^&#]*)").exec(ytplayer.getVideoUrl())[1];
    $.post("/rate",
        { 
            q: document.getElementById("q").value,
            v: v,
            r: rating
        },
        function () {
            if(rating==1) document.getElementById("liked").style.visibility="visible";
            else document.getElementById("liked").style.visibility="hidden";
        }
    );
}
