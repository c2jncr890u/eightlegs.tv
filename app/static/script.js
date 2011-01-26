function skip()
{
    var player = document.getElementById("player-object");    
    var v = new RegExp("[\\?&]v=([^&#]*)").exec(player.getVideoUrl())[1];
    window.location = "/?v="+v+"&q="+encodeURIComponent(document.getElementById("q").value);
}
function maybeskip()
{
    var player = document.getElementById("player-object");
    if(player.getPlayerState()==0) skip();
}
function onYouTubePlayerReady(playerid)
{
    var player = document.getElementById("player-object");
    player.addEventListener("onError", "skip" );
    player.addEventListener("onStateChange", "maybeskip" );
}
function rate( rating ){
    var v = new RegExp("[\\?&]v=([^&#]*)").exec(player.getVideoUrl())[1];
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
