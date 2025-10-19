import React from 'react';
import { Line } from 'react-chartjs-2';
import { useState, useEffect } from 'react';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const EnergyChart = ({ data }) => {
  const [chartData, setChartData] = useState({
    labels: data.map(entry => entry.date),
    datasets: [
      {
        label: 'Precio de Energía (€/MWh)',
        data: data.map(entry => entry.price),
        fill: true,
        borderColor: '#8BC34A',
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
  
          if (!chartArea) {
            return null;
          }
  
          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(255, 167, 38, 0.8)'); // Color más intenso arriba
          gradient.addColorStop(1, 'rgba(255, 235, 59, 0.2)'); // Color más suave abajo
  
          return gradient;
        },
        tension: 0.4,
      },
    ],
  });

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Evolución del Precio de la Energía',
      },
      tooltip: {
        callbacks: {
          label: function (tooltipItem) {
            return `Precio: ${tooltipItem.raw} €/MWh`;
          },
        },
      },
    },

    hover: {
      mode: 'nearest',
      intersect: true,
    },
    animation: {
      duration: 1000, // Duración de la animación
      easing: 'easeOutQuart', // Estilo de animación
    },
  };

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulación: Agregar datos dinámicamente
      const newData = {
        date: new Date().toISOString().slice(0, 10), // Fecha actual
        price: Math.random() * 100, // Precio aleatorio
      };
      // const updatedData = [...data, newData];
      const updatedData = data;
      setChartData({
        labels: updatedData.map(entry => entry.date),
        datasets: [
          {
            ...chartData.datasets[0],
            data: updatedData.map(entry => entry.price),
          },
        ],
      });
    }, 10000); // Actualiza cada 5 segundos

    return () => clearInterval(interval); // Limpia el intervalo
  }, [data, chartData.datasets]);


  return <Line data={chartData} options={options} />;
};

export default EnergyChart;

