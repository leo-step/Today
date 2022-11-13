import logo from './logo.svg';
import './App.css';
import Weather from './components/Weather';
import 'bootstrap/dist/css/bootstrap.min.css';
import SneakyLinksTable from "./components/SneakyLinks";

function App() {
  return (
    <div className="App">
      <header className="App-header">

        <Weather></Weather>
          <SneakyLinksTable></SneakyLinksTable>

      </header>
    </div>
  );
}

export default App;
