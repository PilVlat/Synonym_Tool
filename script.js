let newText = "Mary persuades Jack to go to the movies.";
document.getElementById("text").innerText = newText;

let alternatives_scores = null

$(document).ready(function() {
    $('#dropdown').select2({
        placeholder: 'Select or Type',
        allowClear: true
    });
});

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
async function get_data_fake() {
    return [[8,2,3,8,2,3,8,2,3,8,2,3],[999,1023813,39183,999,1023813,39183,999,1023813,39183,999,1023813,39183],["Hello", "Blue", "Bag","Hello", "Blue", "Bag","Hello", "Blue", "Bag","Hello", "Blue", "Bag"]]
}

async function table() {
    const element = document.getElementById("refresh")
    element.classList.add("animate-spin")
    element.classList.remove("shadow-xl")
    const [usage,match_count,word] = await get_data()
    table_element = document.getElementById("table")
    console.log(table)
    empty_table = document.createElement("tbody")
    empty_table.id = "table"
    table_element.replaceWith(empty_table)
    const max_usage = Math.max(...usage)
    const max_match_count = Math.max(...match_count)
    for (let i = 0; i < usage.length; i++) {
        const new_line = document.createElement("tr")
        const usage_field = document.createElement("td")
        const match_count_field = document.createElement("td")
        const word_field = document.createElement("td")
        new_line.className = "text-white"
        empty_table.appendChild(new_line)
        usage_field.textContent = usage[i]
        match_count_field.textContent = match_count[i]
        word_field.textContent = word[i]
        usage_field.className = `px-1 bg-[rgb(${255*(usage[i]/max_usage)},${255-255*(usage[i]/max_usage)},0)]`
        match_count_field.className = `px-1 bg-[rgb(${255*((match_count[i]/max_match_count)**(1/5))},${255-255*((match_count[i]/max_match_count)**(1/5))},0)]`
        console.log(match_count[i], 255*(match_count[i]/max_match_count))
        word_field.className = `px-1 bg-[rgb(${255*((match_count[i]/max_match_count+usage[i]/max_usage))/2},${255-255*((match_count[i]/max_match_count+usage[i]/max_usage))/2},0)]`
        new_line.appendChild(usage_field)
        new_line.appendChild(match_count_field)
        new_line.appendChild(word_field)
    }
    element.classList.remove("animate-spin")
    element.classList.add("shadow-xl")
    find_sentences()
}

function find_sentences() {
    const original_sentences = document.getElementById("sentences-highlighted") 
    let sentences_field = document.createElement("div")
    sentences_field.className = "overflow-scroll h-9/10"
    sentences_field.id = "sentences-highlighted"
    // Get the input element
    const inputField = document.getElementById('input-word');
    
    const inputValue = inputField.value;
    
    let text = document.getElementById('text').value;
    // text = "\n" + text + "\n"
    // text_lower = text.toLowerCase()
    const reg_exp = RegExp(`(?:^|(?<=[.!?]\\s))[^.!?]*?\\b${inputValue}\\b[^.!?]*?[.!?]`, "gi")
    let iterator = text.matchAll(reg_exp)
    for (const match of iterator) {
        let line = document.createElement("p")
        line.innerText = match
        line.className = "text-gray-800"

        line.addEventListener('click', function() {replace_word(inputValue, match)}) 
        sentences_field.appendChild(line)
    }
    original_sentences.replaceWith(sentences_field)
}
function get_sliders() {
    const similarity_slid = document.getElementById("similarity_slider").value
    const grammar_slid = document.getElementById("grammatical_slider").value
    const rare_slid = document.getElementById("rare_slider").value
    return [similarity_slid, grammar_slid, rare_slid]
}
async function display_alternatives() {
    open_alternatives()
    let word_score = new Array()
    const [similarity_slid, grammar_slid, rare_slid] = get_sliders()
    console.log(similarity_slid, grammar_slid, rare_slid)
    for (const key of Object.keys(alternatives_scores)) {
        word_score.push([key, similarity_slid*alternatives_scores[key][0]+grammar_slid*alternatives_scores[key][1]-rare_slid*alternatives_scores[key][2]])
    }
    word_score.sort((a, b) => b[1] - a[1])
    const table_alt = document.getElementById("table_alternatives") 
    const new_table = document.createElement("tbody")
    new_table.id = "table_alternatives"
    for (const values of word_score) {
        const new_line = document.createElement("tr")
        const word = document.createElement("td")
        const score = document.createElement("td")
        new_line.className = "text-white text-center"
        new_table.appendChild(new_line)
        word.textContent = values[0]
        score.textContent = values[1].toFixed(2)
        new_line.appendChild(word)
        new_line.appendChild(score)
    }
    console.log(table_alt)
    console.log(new_table)
    table_alt.replaceWith(new_table)
}

async function replace_word(word, sentence) {
    console.log(`CALLING BACKEND WTH ${word} and ${sentence}`)
    data = {"word":word, "sentence":sentence}
    const response = await fetch("http://localhost:5000/api/alternatives", {
        method:"POST",
        headers:{
            'Authorization': "JfslidfjskfnKfnsdfjlhJfKLFjsinNfskjflshNfsdjhfslfhsjJhfjslfhsldfHu*(#@HfHFSFKHUhfshof)",
            'Content-Type': 'application/json'  // Explicitly set the content type to JSON
        },
        body:JSON.stringify(data),
    })
    const responseData = await response.json();
    alternatives_scores = responseData
    console.log('Success:', responseData);
    display_alternatives()
}

function close_alternatives() {
    alt_window = document.getElementById("alternatives_window")
    alt_window.classList.add("invisible")
}
function open_alternatives() {
    alt_window = document.getElementById("alternatives_window")
    alt_window.classList.remove("invisible")
}
function score() {
    let score = 0 
}
