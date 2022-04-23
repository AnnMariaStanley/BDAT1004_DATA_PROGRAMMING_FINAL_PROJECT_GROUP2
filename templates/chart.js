getData()

function getData(){
    fetch('/list')
    .then(function (response) {
    return response.json();
    })
    .then(function (res) {
        console.log('GET response:');
        console.log(res[0]); 
    });
}
