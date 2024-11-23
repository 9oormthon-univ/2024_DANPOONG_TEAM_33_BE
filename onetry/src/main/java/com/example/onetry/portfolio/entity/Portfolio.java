package com.example.onetry.portfolio.entity;

import com.example.onetry.common.BaseTimeEntity;
import com.example.onetry.user.entity.User;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

import java.time.LocalDate;

@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "portfolio")
@Getter
public class Portfolio extends BaseTimeEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "portfolio_name")
    private String portfolioName;

    @Column(name = "generateFileName")
    private String generateFileName;

    @Column(name = "certificationPath")
    private String portfolioPath;

    @ManyToOne
    @JoinColumn(name = "user_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;

    @Builder
    protected Portfolio(String portfolioName, String generateFileName, String portfolioPath, User user){
        this.portfolioName = portfolioName;
        this.generateFileName = generateFileName;
        this.portfolioPath = portfolioPath;
        this.user = user;
    }
}
