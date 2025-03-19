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
    const [error, setError] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        fetchHighScores()
        // Fetch scores every 5 seconds to keep the display current
        const interval = setInterval(fetchHighScores, 5000)
        return () => clearInterval(interval)
    }, [])

    const fetchHighScores = async () => {
        try {
            const response = await fetch('/api/highscores')
            if (!response.ok) {
                throw new Error('Failed to fetch scores')
            }
            const data = await response.json()
            setHighScores(data)
            setError(null)
        } catch (error) {
            console.error('Error fetching high scores:', error)
            setError('Failed to load scores. Please try again later.')
        } finally {
            setIsLoading(false)
        }
    }

    const submitScore = async (name: string, score: number) => {
        try {
            const response = await fetch('/api/highscores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, score }),
            })
            if (!response.ok) {
                throw new Error('Failed to submit score')
            }
            const data = await response.json()
            setHighScores(data)
            setError(null)
        } catch (error) {
            console.error('Error submitting score:', error)
            alert('Failed to submit score. Please try again.')
        }
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
                    {error ? (
                        <div className="bg-gray-800 p-6 rounded-lg shadow-xl">
                            <div className="text-red-500 text-center p-4">
                                <p className="text-xl mb-4">⚠️</p>
                                <p>{error}</p>
                                <button
                                    onClick={() => {
                                        setError(null);
                                        fetchHighScores();
                                    }}
                                    className="mt-4 px-4 py-2 bg-game-primary rounded hover:bg-opacity-80"
                                >
                                    Retry
                                </button>
                            </div>
                        </div>
                    ) : isLoading ? (
                        <div className="bg-gray-800 p-6 rounded-lg shadow-xl">
                            <div className="text-center p-4">
                                <div className="animate-spin text-4xl mb-4">⚡</div>
                                <p>Loading scores...</p>
                            </div>
                        </div>
                    ) : (
                        <Scoreboard scores={highScores} />
                    )}
                </div>

                <footer className="mt-12 text-center text-gray-400">
                    <p>Built with React, TypeScript, and Flask</p>
                </footer>
            </div>
        </div>
    )
}

export default App