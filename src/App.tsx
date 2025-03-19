import { useState, useEffect } from 'react'
import GameBoard from './components/GameBoard'
import Scoreboard from './components/Scoreboard'

interface HighScore {
    id: number;
    name: string;
    score: number;
    date: string;
}

function App() {
    const [highScores, setHighScores] = useState<HighScore[]>([])

    // Load scores from scores.json on mount
    useEffect(() => {
        fetch('/scores.json')
            .then(response => response.json())
            .then(data => {
                if (data.scores) {
                    setHighScores(data.scores)
                }
            })
            .catch(error => {
                console.error('Error loading scores:', error)
                // If there's an error loading scores.json, try localStorage as fallback
                const savedScores = localStorage.getItem('highScores')
                if (savedScores) {
                    setHighScores(JSON.parse(savedScores))
                }
            })
    }, [])

    const submitScore = (name: string, score: number) => {
        const newScore: HighScore = {
            id: Date.now(),
            name,
            score,
            date: new Date().toISOString()
        }

        const updatedScores = [...highScores, newScore]
            .sort((a, b) => b.score - a.score)
            .slice(0, 10) // Keep only top 10 scores

        setHighScores(updatedScores)
        
        // Save to scores.json
        const scoresData = { scores: updatedScores }
        fetch('/scores.json', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(scoresData, null, 2)
        }).catch(error => {
            console.error('Error saving scores:', error)
            // Fallback to localStorage if saving to file fails
            localStorage.setItem('highScores', JSON.stringify(updatedScores))
        })
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-6xl mx-auto">
                <header className="text-center mb-12">
                    <h1 className="text-5xl font-bold mb-4 text-game-primary">
                        Target Clicker
                    </h1>
                    <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                        Test your reflexes! Click on the moving targets as quickly as possible.
                        You have 30 seconds to achieve the highest score.
                    </p>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <GameBoard onGameOver={submitScore} />
                    <Scoreboard scores={highScores} />
                </div>

                <footer className="mt-12 text-center text-gray-400">
                    <p>Built with React and TypeScript</p>
                </footer>
            </div>
        </div>
    )
}

export default App