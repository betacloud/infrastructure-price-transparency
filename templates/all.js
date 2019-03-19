var ctx = document.getElementById('all').getContext('2d');
Chart.defaults.global.defaultFontFamily = "'Montserrat', sans-serif";
Chart.defaults.global.defaultFontColor = "#79838c";
var chart = new Chart(ctx, {
    // The type of chart we want to create
    type: 'line',

    // The data for our dataset
    data: {
        labels: [{{ labels }}],
        datasets: [
          {
              label: "Betacloud",
              pointRadius: 0,
              borderWidth: 2,
              tension: 0,
              fill: false,
              data: [{{ betacloud_data }}],
          },
          {
              label: "Netways",
              pointRadius: 0,
              borderWidth: 2,
              tension: 0,
              fill: false,
              data: [{{ netways_data }}],
          },
          {
              label: "Teutostack",
              pointRadius: 0,
              borderWidth: 3,
              tension: 0,
              fill: false,
              data: [{{ teutostack_data }}],
          },
          {
              label: "OVH",
              pointRadius: 0,
              borderWidth: 3,
              tension: 0,
              fill: false,
              data: [{{ ovh_data }}],
          },
          {
              label: "Citycloud",
              pointRadius: 0,
              borderWidth: 3,
              tension: 0,
              fill: false,
              data: [{{ citycloud_data }}],
          },
          {
              label: "Google",
              pointRadius: 0,
              borderWidth: 3,
              tension: 0,
              fill: false,
              data: [{{ google_data }}],
          },
          {
              label: "AWS",
              pointRadius: 0,
              borderWidth: 3,
              tension: 0,
              fill: false,
              data: [{{ aws_data }}],
          },
          {
              label: "Azure",
              pointRadius: 0,
              borderWidth: 3,
              tension: 0,
              fill: false,
              data: [{{ azure_data }}],
          },
          {
              label: "OTC",
              pointRadius: 0,
              borderWidth: 3,
              tension: 0,
              fill: false,
              data: [{{ otc_data }}],
          }
        ]
    },

    // Configuration options go here
    options: {
      plugins: {
        colorschemes: {
          // https://nagix.github.io/chartjs-plugin-colorschemes/colorchart.html
          scheme: 'tableau.Classic10'
        }
      },
      responsive: true,
      title:{
          display: true,
          position: 'bottom',
          text: 'Letzte Aktualisierung am {{ today }}.',
          fontSize: 12,
          fontStyle: 'normal'
      },
      legend: {
        position: 'bottom',
        labels: {
          fontSize: 14,
          padding: 15,
        }
      },
      tooltips: {
          mode: 'index',
          intersect: false,
          bodySpacing: 5
      },
      hover: {
          mode: 'nearest',
          intersect: true
      },
      scales: {
          xAxes: [{
              display: true,
              ticks: {
                  stepSize: 1,
                  min: 0,
                  autoSkip: false
              }
          }],
          yAxes: [{
              display: true,
              scaleLabel: {
                  display: true,
                  labelString: 'Preis / Stunde [Euro]',
                  fontSize: 14,
              },
              ticks: {
                    beginAtZero: true,
              }
          }]
      }
  }
});
