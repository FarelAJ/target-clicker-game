import { useState, useEffect } from 'react';

interface ScoreboardProps {
    scores: Array<{
        id: number;
        name: string;
        score: number;
        date: string;
    }>;
}

const Scoreboard: React.FC<ScoreboardProps> = ({ scores }) => {
    const [newScore, setNewScore] = useState<number | null>(null);

    // Sort scores by score value (descending) and take top 5
    const sortedScores = [...scores]
        .sort((a, b) => b.score - a.score)
        .slice(0, 5);

    useEffect(() => {
        if (scores.length > 0) {
            // Get the most recently added score (highest ID)
            const latestScore = scores.reduce((latest, current) =>
                current.id > latest.id ? current : latest
            );
            setNewScore(latestScore.score);
            const timer = setTimeout(() => setNewScore(null), 2000);
            return () => clearTimeout(timer);
        }
    }, [scores]);

    const getStats = () => {
        if (scores.length === 0) return null;
        return {
            highestScore: Math.max(...scores.map(s => s.score)),
            averageScore: Math.round(scores.reduce((acc, s) => acc + s.score, 0) / scores.length),
            totalGames: scores.length
        };
    };

    const stats = getStats();

    return (
        <div className="bg-gray-800 p-6 rounded-lg shadow-xl h-full">
            <h2 className="text-3xl font-bold mb-6 text-game-primary text-center">
                Top 5 Scores
            </h2>

            {stats && (
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-gray-700 p-4 rounded-lg text-center">
                        <div className="text-game-secondary text-sm">Highest</div>
                        <div className="text-xl font-bold">{stats.highestScore}</div>
                    </div>
                    <div className="bg-gray-700 p-4 rounded-lg text-center">
                        <div className="text-game-secondary text-sm">Average</div>
                        <div className="text-xl font-bold">{stats.averageScore}</div>
                    </div>
                    <div className="bg-gray-700 p-4 rounded-lg text-center">
                        <div className="text-game-secondary text-sm">Games</div>
                        <div className="text-xl font-bold">{stats.totalGames}</div>
                    </div>
                </div>
            )}

            {scores.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-[300px] bg-gray-700 rounded-lg p-6">
                    <p className="text-xl text-gray-300 text-center">
                        No scores yet. Be the first to play!
                    </p>
                    <div className="mt-4 animate-bounce text-game-secondary text-4xl">
                        👆
                    </div>
                </div>
            ) : (
                <div className="space-y-3">
                    {sortedScores.map((score, index) => (
                        <div
                            key={score.id}
                            className={`flex justify-between items-center p-4 rounded-lg transition-all ${score.score === newScore
                                ? 'animate-pulse bg-game-primary/20 border border-game-primary'
                                : index === 0
                                    ? 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border border-yellow-500/50'
                                    : index === 1
                                        ? 'bg-gradient-to-r from-gray-400/20 to-gray-500/20 border border-gray-400/50'
                                        : index === 2
                                            ? 'bg-gradient-to-r from-orange-700/20 to-orange-800/20 border border-orange-700/50'
                                            : 'bg-gray-700'
                                }`}
                        >
                            <div className="flex items-center gap-4">
                                <span className={`text-2xl font-bold ${index === 0
                                    ? 'text-yellow-500'
                                    : index === 1
                                        ? 'text-gray-400'
                                        : index === 2
                                            ? 'text-orange-700'
                                            : 'text-game-secondary'
                                    }`}>
                                    #{index + 1}
                                </span>
                                <div>
                                    <span className="text-lg">{score.name}</span>
                                    <div className="text-xs text-gray-400">
                                        {new Date(score.date).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>
                            <span className="text-xl font-bold text-game-primary">
                                {score.score}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Scoreboard;