package com.example.onetry.resume.entity;

import com.example.onetry.common.BaseTimeEntity;
import com.example.onetry.resume.dto.req.ResumeUpdateDto;
import com.example.onetry.user.entity.User;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "resume")
@Getter
public class Resume extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String idPhotoUrl;
    private String name;
    private String nationalId;
    private LocalDate birthDate;
    private String address;
    private String email;

    @OneToOne
    @JoinColumn(name="user_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;

    @Builder
    protected Resume(String email,User user,String idPhotoUrl){
        this.email = email;
        this.user = user;
        this.idPhotoUrl = idPhotoUrl;
    }

    public void updateFromDto(ResumeUpdateDto dto) {
        if (dto.name() != null) this.name = dto.name();
        if (dto.address() != null) this.address = dto.address();
        if (dto.birthDate() != null) this.birthDate = dto.birthDate();
        if (dto.nationalId() != null) this.nationalId = dto.nationalId();
    }

    public void updateIdPhotoUrl(String updateFilePath){
        this.idPhotoUrl = updateFilePath;
    }

}
