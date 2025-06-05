let newText = `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas ullamcorper lacus risus, eu lacinia neque rhoncus et. Ut dapibus malesuada velit et ultricies. Integer nec ornare lorem. Ut laoreet elit et ultrices accumsan. Phasellus euismod, lectus id ultricies vulputate, justo tortor ultrices magna, ac vulputate magna ex nec nisi. Phasellus massa lorem, aliquam ac aliquet sed, dignissim id orci. Quisque ac dui leo. Vivamus vulputate at nibh quis ornare. Proin et ante pharetra ex consequat elementum.

Morbi vestibulum nibh non turpis accumsan, vitae congue elit ultrices. Praesent in mattis turpis. Donec nisl est, mattis vitae elit at, porttitor condimentum orci. Maecenas consectetur, massa ut mattis ullamcorper, erat odio posuere arcu, ut venenatis ante metus in felis. Vestibulum eget diam eu leo hendrerit elementum. Sed quis pretium nulla. Quisque lacinia pulvinar felis, eu pulvinar elit ultricies ut. Sed et tincidunt ipsum. Curabitur congue nibh turpis, consectetur condimentum leo imperdiet non.

Maecenas euismod vulputate auctor. Sed blandit elit risus, nec tempor tellus vestibulum vel. Duis euismod urna id tortor sodales, ac facilisis arcu suscipit. Vestibulum venenatis risus a arcu convallis, nec iaculis felis sollicitudin. Pellentesque lacinia metus eget quam sagittis gravida. Ut vestibulum massa eu enim faucibus, at rhoncus metus placerat. Curabitur sed ipsum eget est ultricies accumsan non vitae augue. Etiam elementum tristique risus vitae consequat. Donec sit amet feugiat orci, et congue tellus. Lorem ipsum dolor sit amet, consectetur adipiscing elit.

Vestibulum feugiat ac dolor nec fermentum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Nam aliquet risus id nisi volutpat accumsan. Aliquam ut felis eget urna placerat consequat. Morbi pretium lectus id imperdiet suscipit. Duis felis enim, efficitur quis venenatis id, mollis nec nisl. In rutrum nunc ut consectetur mattis. Phasellus nibh ligula, aliquam id odio pretium, tempus efficitur lorem. In diam diam, ullamcorper id accumsan at, suscipit et tortor. In hac habitasse platea dictumst. Nunc id sem sit amet felis sodales venenatis vitae at nulla. Nullam efficitur eleifend massa at dapibus. Cras feugiat ipsum sit amet nunc vestibulum rutrum. Etiam molestie purus eu sodales sollicitudin. Praesent eget mi vel metus bibendum euismod at a urna.

Nullam luctus sem vitae nisl blandit iaculis. Quisque facilisis ac mauris eget blandit. Etiam ut feugiat nulla. Phasellus aliquet dignissim sodales. Pellentesque tortor leo, ultrices nec varius eu, dignissim in velit. Nam eleifend posuere nisi at gravida. Donec vehicula risus vitae tortor feugiat sagittis. Duis rutrum, quam vitae rutrum efficitur, nisl nibh mattis tellus, sit amet tempor risus velit id velit. Vestibulum quis ipsum quis lorem pretium porta. Duis venenatis sem mi. Aenean malesuada bibendum orci, ut aliquet nunc. Curabitur pellentesque, est et commodo volutpat, turpis magna convallis massa, sed vehicula tortor orci et risus. Phasellus luctus arcu nunc, euismod tempus dui laoreet ac. In ex elit, molestie non enim ac, cursus dapibus dolor. Sed vel augue mollis, vestibulum orci sit amet, convallis turpis.
`;
document.getElementById("text").value = newText;

$(document).ready(function() {
    $('#dropdown').select2({
        placeholder: 'Select or Type',
        allowClear: true
    });
});

function update() {
    // Get the input element
    const inputField = document.getElementById('input-word');
    
    // Retrieve its value
    const inputValue = inputField.value;
    
    // Display the value (for demonstration)
    document.getElementById('text').value = `You entered: ${inputValue}`;
}
async function sendText() {
    var text = document.getElementById('text').value;  // Get the value of the textarea
    var data = {
        text:text
    };
    const response = await fetch("http://localhost:5000/api/graph", {
        method:"POST",
        headers:{
            'Authorization': "JfslidfjskfnKfnsdfjlhJfKLFjsinNfskjflshNfsdjhfslfhsjJhfjslfhsldfHu*(#@HfHFSFKHUhfshof)",
            'Content-Type': 'application/json'  // Explicitly set the content type to JSON
        },
        body:JSON.stringify(data),
    })
    const responseData = await response.json();
    console.log('Success:', responseData);
    return responseData
}
async function get_data() {
    const data = await sendText();
    console.log(data)
    let x = []
    let y = []
    let labels = []
    data.sorted_occurences.forEach((item, index) => {
        labels.push(item[0])
        x.push(item[1])
        y.push(data.match_count[item[0]])
        console.log(item[0], item[1], data.match_count[item[0]])
    });
    console.log(x, y, labels)
    return [x, y, labels]
}
async function chart() {
    const [x,y,labels] = await get_data()
    var data = [{
        x: x,
        y: y,
        mode: 'markers+text',
        type: 'scatter',
        text: labels,
        textposition: 'top center',
        textfont: {size: 10},      
        marker: { size: 2, color: 'rgb(75, 192, 192)' }
    }];

    var layout = {
        title: 'Scatter Plot with Labels',
        xaxis: {
            title: 'X Axis',
        },
        yaxis: {
            title: 'Y Axis',
        }
    };

    Plotly.newPlot('graph-div', data, layout);
}
async function table() {
    const element = document.getElementById("refresh")
    element.classList.add("animate-spin-fast")
    element.classList.remove("shadow-xl")
    setTimeout(() => {
        console.log("Hello my friend")
        element.classList.remove("animate-spin-fast")
        element.classList.add("shadow-xl")},
        2000)
}

