import { Routes, Route, Link, NavLink } from 'react-router-dom'
import { Navbar, Container, Nav } from 'react-bootstrap'
import HomePage from './pages/HomePage'
import SchemesPage from './pages/SchemesPage'
import MatchPage from './pages/MatchPage'

export default function App() {
  return (
    <div className="d-flex flex-column min-vh-100 bg-light">
      <Navbar bg="dark" variant="dark" expand="md" sticky="top">
        <Container>
          <Navbar.Brand as={Link} to="/" className="fw-bold">
            SchemeGuide
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="main-nav" />
          <Navbar.Collapse id="main-nav">
            <Nav className="ms-auto gap-1">
              <Nav.Link as={NavLink} to="/schemes">Browse Schemes</Nav.Link>
              <Nav.Link as={NavLink} to="/check">Check Eligibility</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <main className="flex-grow-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/schemes" element={<SchemesPage />} />
          <Route path="/check" element={<MatchPage />} />
        </Routes>
      </main>

      <footer className="bg-dark text-secondary py-3 text-center small">
        <Container>
          SchemeGuide — Open source. Data sourced from official government portals only.
        </Container>
      </footer>
    </div>
  )
}
