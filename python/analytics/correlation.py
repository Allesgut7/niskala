# Niskala - Correlation Analysis
# Version: 1.0.0
# Stock-to-stock and sector correlation with clustering

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import logging


@dataclass
class CorrelationResult:
    """Correlation analysis result"""
    symbol1: str
    symbol2: str
    correlation: float
    p_value: float
    relationship: str  # 'strong_positive', 'positive', 'neutral', 'negative', 'strong_negative'


@dataclass
class ClusterResult:
    """Cluster analysis result"""
    cluster_id: int
    symbols: List[str]
    avg_correlation: float
    representative: str  # Most central stock


class CorrelationAnalyzer:
    """Analyze correlations between stocks and sectors"""
    
    def __init__(self):
        logging.info("Correlation analyzer initialized")
    
    def calculate_correlation_matrix(
        self,
        returns: pd.DataFrame,
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """Calculate correlation matrix
        
        Args:
            returns: DataFrame of daily returns (columns = symbols)
            method: 'pearson', 'spearman', or 'kendall'
            
        Returns:
            Correlation matrix DataFrame
        """
        return returns.corr(method=method)
    
    def find_correlated_pairs(
        self,
        returns: pd.DataFrame,
        threshold: float = 0.7,
        method: str = 'pearson'
    ) -> List[CorrelationResult]:
        """Find highly correlated stock pairs
        
        Args:
            returns: DataFrame of daily returns
            threshold: Minimum absolute correlation
            method: Correlation method
            
        Returns:
            List of CorrelationResult for correlated pairs
        """
        corr_matrix = self.calculate_correlation_matrix(returns, method)
        pairs = []
        
        symbols = corr_matrix.columns.tolist()
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = corr_matrix.iloc[i, j]
                
                if abs(corr) >= threshold:
                    # Classify relationship
                    if corr >= 0.8:
                        relationship = 'strong_positive'
                    elif corr >= 0.5:
                        relationship = 'positive'
                    elif corr <= -0.8:
                        relationship = 'strong_negative'
                    elif corr <= -0.5:
                        relationship = 'negative'
                    else:
                        relationship = 'neutral'
                    
                    pairs.append(CorrelationResult(
                        symbol1=symbols[i],
                        symbol2=symbols[j],
                        correlation=float(corr),
                        p_value=0.0,  # Would need scipy.stats for this
                        relationship=relationship
                    ))
        
        # Sort by absolute correlation
        pairs.sort(key=lambda p: abs(p.correlation), reverse=True)
        
        logging.info(f"Found {len(pairs)} correlated pairs (threshold={threshold})")
        
        return pairs
    
    def cluster_stocks(
        self,
        returns: pd.DataFrame,
        n_clusters: int = 5,
        method: str = 'single'
    ) -> List[ClusterResult]:
        """Cluster stocks by correlation similarity
        
        Args:
            returns: DataFrame of daily returns
            n_clusters: Number of clusters
            method: Linkage method ('single', 'complete', 'average', 'ward')
            
        Returns:
            List of ClusterResult objects
        """
        # Calculate distance matrix (1 - correlation)
        corr_matrix = self.calculate_correlation_matrix(returns)
        dist_matrix = 1 - corr_matrix.abs()
        
        # Ensure diagonal is 0
        np.fill_diagonal(dist_matrix.values, 0)
        
        # Hierarchical clustering
        condensed_dist = squareform(dist_matrix.values)
        link = linkage(condensed_dist, method=method)
        
        # Cut dendrogram into clusters
        cluster_labels = fcluster(link, n_clusters, criterion='maxclust')
        
        # Organize into clusters
        symbols = corr_matrix.columns.tolist()
        clusters = {}
        
        for symbol, label in zip(symbols, cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(symbol)
        
        # Build results
        results = []
        for cluster_id, cluster_symbols in clusters.items():
            # Calculate average intra-cluster correlation
            cluster_corr = corr_matrix.loc[cluster_symbols, cluster_symbols]
            avg_corr = (cluster_corr.sum().sum() - len(cluster_symbols)) / (len(cluster_symbols) * (len(cluster_symbols) - 1))
            
            # Find most central stock (highest average correlation with others)
            central_scores = cluster_corr.mean()
            representative = central_scores.idxmax()
            
            results.append(ClusterResult(
                cluster_id=int(cluster_id),
                symbols=cluster_symbols,
                avg_correlation=float(avg_corr),
                representative=representative
            ))
        
        # Sort by cluster size
        results.sort(key=lambda c: len(c.symbols), reverse=True)
        
        logging.info(f"Clustered {len(symbols)} stocks into {len(results)} groups")
        
        return results
    
    def sector_correlation(
        self,
        returns: pd.DataFrame,
        sector_mapping: Dict[str, List[str]]
    ) -> pd.DataFrame:
        """Calculate sector-level correlations
        
        Args:
            returns: DataFrame of daily returns
            sector_mapping: Dict mapping sector -> list of symbols
            
        Returns:
            Correlation matrix of sector returns
        """
        # Calculate sector returns (equal-weighted)
        sector_returns = pd.DataFrame()
        
        for sector, symbols in sector_mapping.items():
            valid_symbols = [s for s in symbols if s in returns.columns]
            if valid_symbols:
                sector_returns[sector] = returns[valid_symbols].mean(axis=1)
        
        return sector_returns.corr()
    
    def rolling_correlation(
        self,
        returns: pd.DataFrame,
        symbol1: str,
        symbol2: str,
        window: int = 60
    ) -> pd.Series:
        """Calculate rolling correlation between two stocks
        
        Args:
            returns: DataFrame of daily returns
            symbol1: First stock symbol
            symbol2: Second stock symbol
            window: Rolling window size (days)
            
        Returns:
            Series of rolling correlations
        """
        return returns[symbol1].rolling(window).corr(returns[symbol2])
    
    def find_diversification_pairs(
        self,
        returns: pd.DataFrame,
        n_pairs: int = 5
    ) -> List[CorrelationResult]:
        """Find stock pairs with lowest correlation (best diversification)
        
        Args:
            returns: DataFrame of daily returns
            n_pairs: Number of pairs to return
            
        Returns:
            List of CorrelationResult for diversification pairs
        """
        corr_matrix = self.calculate_correlation_matrix(returns)
        pairs = []
        
        symbols = corr_matrix.columns.tolist()
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                pairs.append(CorrelationResult(
                    symbol1=symbols[i],
                    symbol2=symbols[j],
                    correlation=float(corr_matrix.iloc[i, j]),
                    p_value=0.0,
                    relationship='diversification'
                ))
        
        # Sort by lowest correlation (best diversification)
        pairs.sort(key=lambda p: p.correlation)
        
        return pairs[:n_pairs]


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample returns
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='B')
    
    # Create correlated stocks
    base = np.random.randn(len(dates)) * 0.02
    
    returns = pd.DataFrame({
        'BBCA': base + np.random.randn(len(dates)) * 0.005,
        'BBRI': base + np.random.randn(len(dates)) * 0.006,
        'BMRI': base + np.random.randn(len(dates)) * 0.005,
        'TLKM': np.random.randn(len(dates)) * 0.015,  # Less correlated
        'GOTO': np.random.randn(len(dates)) * 0.025,  # Different sector
    }, index=dates)
    
    analyzer = CorrelationAnalyzer()
    
    # Correlation matrix
    print("=== Correlation Matrix ===")
    corr = analyzer.calculate_correlation_matrix(returns)
    print(corr.round(2))
    
    # Correlated pairs
    print("\n=== Highly Correlated Pairs (|r| > 0.5) ===")
    pairs = analyzer.find_correlated_pairs(returns, threshold=0.5)
    for p in pairs:
        print(f"  {p.symbol1} - {p.symbol2}: {p.correlation:.2f} ({p.relationship})")
    
    # Clustering
    print("\n=== Stock Clusters ===")
    clusters = analyzer.cluster_stocks(returns, n_clusters=2)
    for c in clusters:
        print(f"  Cluster {c.cluster_id}: {c.symbols} (avg corr: {c.avg_correlation:.2f})")
    
    # Diversification pairs
    print("\n=== Best Diversification Pairs ===")
    div_pairs = analyzer.find_diversification_pairs(returns, n_pairs=3)
    for p in div_pairs:
        print(f"  {p.symbol1} - {p.symbol2}: {p.correlation:.2f}")
