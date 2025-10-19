import React, { useState } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import { TailSpin } from 'react-loader-spinner';
import LogingOut from "../router/LogingOut";

const SummaryBox = ({ title, value }) => {
    // Inline styles para cada cuadro
    const boxStyle = {
      backgroundColor: "#4a4a8a",
      color: "#fff",
      padding: "20px",
      borderRadius: "8px",
      textAlign: "center",
      width: "150px",
      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    };
  
    const titleStyle = {
      fontSize: "18px",
      marginBottom: "10px",
    };
  
    const valueStyle = {
      fontSize: "24px",
      fontWeight: "bold",
    };
  
    return (
      <div style={boxStyle}>
        <h3 style={titleStyle}>{title}</h3>
        <div style={valueStyle}>{value}</div>
      </div>
    );
  };

function PreciosForm() {
    const [desde, setDesde] = useState('');
    const [hasta, setHasta] = useState('');
    const [mercado, setMercado] = useState('');
    const [data, setData] = useState([]);  // Estado para guardar los datos de la tabla
    const [headers, setHeaders] = useState([]);  // Estado para las cabeceras dinámicas
    const [filtros, setFiltros] = useState({}); //Estado para guardar los filtros
    const [loading, setLoading] = useState(false); // Controla el estado de carga
    const [priceStats, setPriceStats] = useState({
        min: 0,
        average: 0,
        max: 0,
      });
    const params = useParams();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true); // Mostrar el spinner
        const data = { desde, hasta, mercado };

        try {
            const response = await fetch('http://127.0.0.1:8000/market-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            const result = await response.json();
            console.log('Precios recibidos:', result);
            if (result.length > 0) {
                setData(result);  // Guarda los datos recibidos en el estado
                setHeaders(Object.keys(result[0]));  // Extrae las cabeceras dinámicamente
                
                // Calcular precios
                const prices = result.map((item) => item.Precio_Español);
                const min = Math.min(...prices);
                const max = Math.max(...prices);
                const average = prices.reduce((a, b) => a + b, 0) / prices.length;

                setPriceStats({ min, average: average.toFixed(2), max });
            }
        } catch (error) {
            console.error('Error al obtener los precios:', error);
        } finally {
            setLoading(false); // Ocultar el spinner
        }
    };

    //Función para buscar de nuevo
    const handleNewSearch = () => {
        console.log("Nueva búsqueda iniciada");
    };

    //Función para limpiar la tabla cada vez que se cambie el desde
    const handleFechaDesdeChange = (e) => {
        setDesde(e.target.value);
        setData([]); // Reinicia la tabla
    };

    //Función para limpiar la tabla cada vez que se cambie el hasta
    const handleFechaHastaChange = (e) => {
        setHasta(e.target.value);
        setData([]); // Reinicia la tabla
    };


    // Función para descargar los datos como CSV
    const downloadCSV = () => {
        // const headers = ["Fecha", "Mes", "Hora", "Season", "Tipo", "Precio_Español"]; // Asegúrate de usar los caracteres correctos aquí
        const rows = data.map(item => Object.values(item));

        // BOM for UTF-8
        let csvContent = "\uFEFF" + headers.join(",") + "\n"
            + rows.map(e => e.join(",")).join("\n");

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", "precios.csv");
        document.body.appendChild(link);

        link.click();
        document.body.removeChild(link);
    };

    // Función para manejar el cambio de los filtros
    const handleFilterChange = (e, header) => {
        const { value } = e.target;
        setFiltros(prevFiltros => ({
            ...prevFiltros,
            [header]: value,
        }));
    };

    // Filtrar los datos basados en los filtros
    const filteredData = data.filter(item => {
        return headers.every(header => {
            if (!filtros[header]) return true;
            return String(item[header]).toLowerCase().includes(filtros[header].toLowerCase());
        });
    });


    return (
        <LogingOut>
            <div className="flex flex-col items-center min-h-screen w-full box-border">
                <form onSubmit={handleSubmit} style={formStyle}>
                    <label style={labelStyle}>
                        {/* <h1 className='text'>Desde: </h1> */}
                        Desde:
                        <input
                            type="date"
                            value={desde}
                            className="block py-2 px-3 mb-4 w-full text-black"
                            onChange={handleFechaDesdeChange}
                            style={inputStyle}
                        />
                    </label>

                    <label style={labelStyle}>
                        Hasta:
                        <input
                            type="date"
                            value={hasta}
                            className="block py-2 px-3 mb-4 w-full text-black"
                            onChange={handleFechaHastaChange}
                            style={inputStyle}
                        />
                    </label>

                    <label style={labelStyle}>
                        Mercado:
                        <select
                            value={mercado}
                            className="block py-2 px-3 mb-4 w-full text-black"
                            onChange={(e) => setMercado(e.target.value)}
                            style={inputStyle}
                        >
                            <option value="">Seleccionar Operador</option>
                            <option value="mercado1">Mercado OMIE</option>
                            <option value="mercado2">ESIOS</option>
                        </select>
                    </label>
                    <button
                        type="submit"
                        style={buttonStyle}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = buttonHoverStyle.backgroundColor}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = buttonStyle.backgroundColor}>
                        Obtener Precios
                    </button>
                    <button
                        type="button"
                        style={buttonStyle}
                        onClick={downloadCSV}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = buttonHoverStyle.backgroundColor}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = buttonStyle.backgroundColor}>
                        Descargar CSV
                    </button>
                </form>

                {/* Aquí puedes añadir tu formulario y el botón para obtener los datos */}
                {loading ? (
                    <div className='flex justify-center bg-center'>
                        <TailSpin color="#00BFFF" height={80} width={80} />
                    </div>

                ) :
                    data.length > 0 ? (
                        <div>
                            <style>{responsiveStyles}</style>  {/* Añade los estilos de responsividad */}
                            <div style={tableContainerStyle}>
                                <table style={tableStyle}>
                                    <thead>
                                        <tr>
                                            {headers.map((header, index) => (
                                                <th key={index} style={thStyle}>
                                                    {header}
                                                    <input
                                                        type="text"
                                                        value={filtros[header] || ''}
                                                        onChange={(e) => handleFilterChange(e, header)}
                                                        placeholder={`Filtrar por ${header}`}
                                                        style={inputStyle}
                                                    />
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredData.map((item, index) => (
                                            <tr key={index}>
                                                {headers.map((header, i) => (
                                                    <td key={i} style={tdStyle}>
                                                        {item[header]}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                    ) : (
                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "center",
                                justifyContent: "center",
                                height: "80vh",
                                textAlign: "center",
                                color: "#ffffff",
                            }}
                        >
                            <h2 style={{ fontSize: "2rem", marginBottom: "20px" }}>
                                No hay datos disponibles
                            </h2>
                            <p style={{ fontSize: "1.2rem", maxWidth: "600px" }}>
                                Por favor, selecciona un rango de fechas y un mercado para mostrar los datos.
                                Puedes comenzar utilizando los filtros superiores.
                            </p>
                            <img
                                src="src/assets/no_data.webp" // Reemplaza con una imagen relevante
                                alt="Sin datos"
                                style={{ width: "250px", marginTop: "20px" }}
                            />
                            <button
                                type="button"
                                style={{
                                    marginTop: "20px",
                                    padding: "10px 20px",
                                    backgroundColor: "#FFA500",
                                    color: "black",
                                    border: "none",
                                    borderRadius: "5px",
                                    cursor: "pointer",
                                }}
                                onClick={handleNewSearch}
                                onMouseOver={(e) => e.currentTarget.style.backgroundColor = buttonHoverStyle.backgroundColor}
                                onMouseOut={(e) => e.currentTarget.style.backgroundColor = buttonStyle.backgroundColor}
                            >
                                Realizar nueva búsqueda
                            </button>
                        </div>

                    )}
                {/* Cuadros resumen */}
                <div style={summarySectionStyle}>
                    <SummaryBox title="Precio Min" value={priceStats.min} />
                    <SummaryBox title="Precio Medio" value={priceStats.average} />
                    <SummaryBox title="Precio Max" value={priceStats.max} />
                </div>

                <section   className="flex justify-center bg-center text-white font-bold rounded mt-2"
                    style={{
                        textAlign: "center",
                        fontSize: "20px", // Aumenta el tamaño del texto
                        marginTop: "20px", // Separa más el título de los cuadros
                        padding: "10px", // Añade espacio dentro del título
                        backgroundColor: "#4a4a8a", // Fondo acorde al diseño general
                        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)", // Sombra para destacar
                        borderRadius: "8px", // Bordes redondeados
                    }}>
                    WAC CROSS-CUTTING SOLUTIONS 
                </section>
            </div>
        </LogingOut>

    );
}


// Estilos en línea
const formStyle = {
    display: 'flex',
    flexDirection: window.innerWidth > 768 ? "row" : "column",
    flexWrap: 'wrap',  // Aseguramos que los elementos se alineen en filas en pantallas pequeñas
    justifyContent: "center", // Centra horizontalmente
    alignItems: "center", // Centra verticalmente
    gap: "20px", // Espaciado entre los elementos
    padding: "20px", // Espacio alrededor
    width: "90%", // Ocupa todo el ancho
};


// Para pantallas grandes, alineamos en fila
const labelStyle = {
    marginRight: '10px',
    color: 'white',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    flex: '1',  // Permite que los inputs y selects se distribuyan en fila
};

const inputStyle = {
    marginTop: '3px',
    width: '100%',
    padding: '1px',
    borderRadius: '4px', // Bordes redondeados
    border: '1px solid #ccc', // Color de borde gris claro
    backgroundColor: '#f0f0f5', // Fondo del input más claro
    color: '#333', // Color de texto oscuro
};

const buttonStyle = {
    padding: '10px 15px',
    backgroundColor: '#fff',  // Color morado para el fondo de los botones '#6C63FF'
    borderRadius: '5px',
    border: 'none',
    color: 'black',
    cursor: 'pointer',
    flex: '1',  // El botón también ocupará un espacio horizontal en pantallas grandes
    transition: 'background-color 0.3s ease',  // Suaviza el cambio de color en el hover
};

// Estilo hover personalizado para los botones
const buttonHoverStyle = {
    backgroundColor: '#4C4B9F',  // Color más oscuro cuando pasas el ratón
};



// Media Queries para pantallas pequeñas
const mediaQueries = `
@media (max-width: 768px) {
  .formStyle {
    flex-direction: column;  // En pantallas pequeñas, los elementos se alinean en columna
  }

  .labelStyle, .inputStyle, .buttonStyle {
    width: 100%;  // Los inputs, selects y el botón ocuparán todo el ancho en pantallas pequeñas
  }
}
`;

const tableContainerStyle = {
    // height: 'auto',  // Permitir que el contenedor ajuste su tamaño
    // maxHeight: '46vw',  // Aumentar la altura máxima del contenedor
    maxHeight: '500px',  // Aumentar la altura máxima del contenedor
    overflowY: 'scroll',  // Habilitar el scroll vertical
    overflowX: 'auto',  // Habilita el scroll horizontal en pantallas pequeñas
    marginTop: '20px',
    width: '93%',  // Ancho completo en pantallas grandes
    maxWidth: '100vw',  // Limita el ancho máximo al ancho de la ventana (viewport)
    margin: '0 auto',  // Centra la tabla
    border: '1px solid #ddd',
    boxSizing: 'border-box',  // Asegura que el padding y border se cuenten dentro del ancho
    // backgroundColor: 'rgba(0, 0, 0, 0.8)',  // Fondo para que contraste con el fondo de la página
};

const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    backgroundColor: 'rgba(0, 0, 0, 0.8)', // Fondo de la tabla semi-transparente
};

const thStyle = {
    padding: '10px',
    backgroundColor: '#3c3c91', // Cambiar color de fondo de las cabeceras
    color: 'white', // Color de texto en blanco
    textAlign: 'left',
    border: '1px solid white',
    position: 'sticky',
    top: '0',
    zIndex: '1',
};


const tdStyle = {
    padding: '10px',
    border: '1px solid white',
    color: 'white',
    textAlign: 'left',
};

// Añadir media queries para manejar el comportamiento en pantallas pequeñas
const responsiveStyles = `
  /* Responsividad en pantallas pequeñas */
  @media (min-width: 391px) and (max-width: 768px) {

    div {
      max-height: 500px;  // Ajuste de altura máxima en pantallas pequeñas
      min-height: 300px;  // Asegura que la tabla no sea demasiado pequeña
      overflow-y: scroll;  // Habilitar scroll vertical
    }
    table {
      width: 100%;  // Ajustar el ancho al 100% en responsive
      max-width: 100vw;  // Limitar el ancho al tamaño de la pantalla
      overflow-x: auto; /* Habilitar scroll horizontal si es necesario */
    }

    th, td {
      font-size: 14px;  // Reducir el tamaño de fuente en móviles
      padding: 8px;  // Reducir el padding para mejorar el espacio
    }
    
  }

  @media (max-width: 480px) {
    th, td {
      font-size: 12px;  // Ajuste aún más pequeño para dispositivos más pequeños
      padding: 4px;  // Reducimos el padding
    }

    table {
      width: 100vw;  // Usamos el 100% del ancho disponible en pantallas pequeñas
      overflow-x: auto;
    }
  }
`;

const summarySectionStyle = {
    display: "flex",
    flexDirection: window.innerWidth > 768 ? "row" : "column",
    flexWrap: 'wrap',  // Aseguramos que los elementos se alineen en filas en pantallas pequeñas
    justifyContent: "space-around",
    padding: "20px",
    marginTop: "20px",
    gap: "20px", // Espaciado entre los cuadros
  };


export default PreciosForm;
