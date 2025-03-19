import { useState, useEffect, useCallback, useRef } from 'react'

interface GameBoardProps {
    onGameOver: (name: string, score: number) => void;
}

const GameBoard: React.FC<GameBoardProps> = ({ onGameOver }) => {
    const [score, setScore] = useState(0)
    const [timeLeft, setTimeLeft] = useState(30)
    const [isPlaying, setIsPlaying] = useState(false)
    const [targetPosition, setTargetPosition] = useState({ x: 50, y: 50 })
    const timerIntervalRef = useRef<NodeJS.Timeout | null>(null)
    const moveFrameRef = useRef<number>(0)
    const targetVelocityRef = useRef({ x: 0, y: 0 })
    const isEndingRef = useRef(false)

    const generateNewPosition = useCallback(() => {
        const x = Math.floor(Math.random() * 80) + 10
        const y = Math.floor(Math.random() * 80) + 10
        setTargetPosition({ x, y })

        // Set new random velocity
        const speed = Math.min(2 + score * 0.2, 5) // Increase speed with score, max 5
        const angle = Math.random() * Math.PI * 2
        targetVelocityRef.current = {
            x: Math.cos(angle) * speed,
            y: Math.sin(angle) * speed
        }
    }, [score])

    const updateTargetPosition = useCallback(() => {
        if (!isPlaying) return

        setTargetPosition(prev => {
            const newX = prev.x + targetVelocityRef.current.x
            const newY = prev.y + targetVelocityRef.current.y

            // Bounce off walls
            if (newX <= 10 || newX >= 90) {
                targetVelocityRef.current.x *= -1
            }
            if (newY <= 10 || newY >= 90) {
                targetVelocityRef.current.y *= -1
            }

            return {
                x: Math.max(10, Math.min(90, newX)),
                y: Math.max(10, Math.min(90, newY))
            }
        })

        moveFrameRef.current = requestAnimationFrame(updateTargetPosition)
    }, [isPlaying])

    const startGame = () => {
        setScore(0)
        setTimeLeft(30)
        setIsPlaying(true)
        isEndingRef.current = false
        generateNewPosition()

        // Start timer
        if (timerIntervalRef.current) {
            clearInterval(timerIntervalRef.current)
        }
        timerIntervalRef.current = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1 && !isEndingRef.current) {
                    endGame()
                    return 0
                }
                return prev - 1
            })
        }, 1000)

        // Start target movement
        updateTargetPosition()
    }

    const endGame = useCallback(() => {
        if (isEndingRef.current) return // Prevent multiple calls
        isEndingRef.current = true
        setIsPlaying(false)

        if (timerIntervalRef.current) {
            clearInterval(timerIntervalRef.current)
        }
        cancelAnimationFrame(moveFrameRef.current)

        const finalScore = score;  // Capture the final score
        console.log('Game Over - Final Score:', finalScore); // Debug log
        const playerName = prompt('Game Over! Enter your name:') || 'Anonymous'
        console.log('Submitting score:', { name: playerName, score: finalScore }); // Debug log
        onGameOver(playerName, finalScore)
    }, [score, onGameOver])

    const handleTargetClick = () => {
        if (!isPlaying) return
        setScore(prev => {
            const newScore = prev + 1;
            console.log('Score increased to:', newScore); // Debug log
            return newScore;
        });
        generateNewPosition()
    }

    useEffect(() => {
        return () => {
            if (timerIntervalRef.current) {
                clearInterval(timerIntervalRef.current)
            }
            cancelAnimationFrame(moveFrameRef.current)
        }
    }, [])

    // Calculate target size based on score
    const targetSize = Math.max(48 - score * 2, 20) // Decrease size with score, min 20px

    return (
        <div className="bg-gray-800 p-6 rounded-lg shadow-xl">
            <div className="flex justify-between items-center mb-6 bg-gray-700 p-4 rounded-lg">
                <div className="text-2xl font-bold text-game-primary">Score: {score}</div>
                <div className="text-2xl font-bold text-game-secondary">Time: {timeLeft}s</div>
            </div>

            {!isPlaying ? (
                <div className="text-center">
                    <h2 className="text-2xl mb-4 text-white">Click Target Game</h2>
                    <p className="text-gray-300 mb-6">
                        Click the moving targets as quickly as you can!<br />
                        Targets get smaller and faster as your score increases.
                    </p>
                    <button
                        onClick={startGame}
                        className="w-full py-4 bg-game-primary hover:bg-indigo-600 rounded-lg transition-all transform hover:scale-105 font-bold text-xl shadow-lg"
                    >
                        Start Game
                    </button>
                </div>
            ) : (
                <div
                    className="relative w-full h-[400px] bg-gray-700 rounded-lg overflow-hidden shadow-inner"
                    style={{ cursor: 'crosshair' }}
                >
                    <button
                        className="absolute bg-game-secondary rounded-full transition-all transform hover:scale-110 shadow-lg animate-pulse"
                        style={{
                            left: `${targetPosition.x}%`,
                            top: `${targetPosition.y}%`,
                            width: `${targetSize}px`,
                            height: `${targetSize}px`,
                            transform: 'translate(-50%, -50%)'
                        }}
                        onClick={handleTargetClick}
                    />
                </div>
            )}
        </div>
    )
}

export default GameBoard