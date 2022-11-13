import logo from './logo.svg';
import './App.css';
import Weather from './components/Weather';
import 'bootstrap/dist/css/bootstrap.min.css';
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from './components/PrinceNews';

function App() {
  return (
    <div className="App">
      <header className="App-header">

        <Weather></Weather>
        <SneakyLinksTable></SneakyLinksTable>
        <PrinceNewsTable></PrinceNewsTable>

      </header>
    </div>
  );
}

export default App;
