
function get_photo(title) {
   let baseUrl =  "http://www.omdbapi.com/?&apikey=925cf197&t=";
   let realUrl = encodeURI(baseUrl+title);
   console.log(realUrl);
   let xhr = new XMLHttpRequest();
   xhr.open("GET", realUrl, true);
   xhr.send();

   xhr.onreadystatechange = function () {
       if(this.readyState == 4 && this.status == 200) {
          let result = JSON.parse(this.responseText);
          document.getElementById(title).src = result["Poster"];
       }
   }
}

function show_photo() {
    let movies = document.getElementById("movies");
    for(let i=0;i<movies.childElementCount;i++) {
        get_photo(movies.children[i].children[1].id);
    }
}





