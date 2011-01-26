function skip()
{
   $.get("/recommend",
      { q: document.getElementById("q").value },
      function ( data ) {
         window.location="/?v="+data+"&q="+encodeURIComponent(document.getElementById("q").value);
      }, "json"
   );   
}
function maybeskip()
{
   if(player.getPlayerState()==0) skip();
}
function onYouTubePlayerReady(playerid)
{
   player = document.getElementById("player");
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
