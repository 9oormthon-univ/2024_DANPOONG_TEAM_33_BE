package com.example.onetry.portfolio.dto.res;

import com.example.onetry.portfolio.entity.Portfolio;
import lombok.Builder;

@Builder
public record PortfolioInfo(
        Long portfolioId,
        String portfolioName,
        String generateFileName
) {
    public static PortfolioInfo of(Portfolio portfolio, String generateFileName){
        return PortfolioInfo.builder()
                .portfolioId(portfolio.getId())
                .portfolioName(portfolio.getPortfolioName())
                .generateFileName(generateFileName)
                .build();
    }
}
